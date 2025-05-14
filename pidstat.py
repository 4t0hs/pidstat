import time
import os
import argparse
from typing import Union, List


CLOCK_TICKS_PER_SECOND = os.sysconf("SC_CLK_TCK")


def jiffies_to_seconds(jiffies: int) -> float:
    """jiffies を秒単位に変換する"""
    return jiffies / CLOCK_TICKS_PER_SECOND


class ProcessBasicInfo:
    """基本的なプロセス情報"""

    def __init__(self):
        self.pid: int = 0 # 1: プロセスID
        self.command: str = ""  # 2: コマンド名 (カッコ付き)
        self.state: str = ""  # 3: プロセス状態 (R, S, D, Z, T, etc.)
        self.parent_pid: int = 0  # 4: 親プロセスID
        self.gid: int = 0  # 5: プロセスグループID
        self.session: int = 0  # 6: セッションID
        self.tty_device_num: int = 0 # 7: 制御端末のメジャー/マイナー番号
        self.tty_gid: int = 0 # 8: 制御端末のフォアグラウンドプロセスグループID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessBasicInfo):
            return False
        return (
            self.pid == other.pid and
            self.command == other.command and
            self.state == other.state and
            self.parent_pid == other.parent_pid and
            self.gid == other.gid and
            self.session == other.session and
            self.tty_device_num == other.tty_device_num and
            self.tty_gid == other.tty_gid
        )

class ProcessCpuTime:
    """[13~16] プロセスCPU時間情報(jiffies単位)"""

    def __init__(self):
        self.user: int = 0 # 13: ユーザーCPU時間
        self.system: int = 0 # 14: システムCPU時間
        self.child_user: int = 0 # 15: 子プロセスのユーザーCPU時間
        self.child_system: int = 0 # 16: 子プロセスのシステムCPU時間

    @property
    def total_cpu_time(self) -> int:
        """合計CPU時間をjiffies単位で返す"""
        return self.user + self.system

    @property
    def total_cpu_time_seconds(self) -> float:
        """合計CPU時間を秒単位で返す"""
        return jiffies_to_seconds(self.total_cpu_time)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessCpuTime):
            return False
        return (
            self.user == other.user and
            self.system == other.system and
            self.child_user == other.child_user and
            self.child_system == other.child_system
        )


class ProcessResourceStat:
    """[21~24] プロセスの資源に関する情報"""

    def __init__(self):
        self.start_time: int = 0  # 21: システム起動後のプロセス開始時間 (jiffies)
        self.virtual_size: int = 0  # 22: 仮想メモリサイズ (バイト)
        self.rss: int = 0  # 23: 常駐セットサイズ (ページ数)
        self.rss_limit: int = 0  # 24: RSS制限 (バイト)

    @property
    def start_time_seconds(self) -> float:
        """プロセス開始時間を秒単位で返す"""
        return jiffies_to_seconds(self.start_time)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessResourceStat):
            return False
        return (
            self.start_time == other.start_time and
            self.virtual_size == other.virtual_size and
            self.rss == other.rss and
            self.rss_limit == other.rss_limit
        )


class PageFaultInfo:
    """[9~12] ベージフォールト関連情報 - 未実装"""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PageFaultInfo):
            return False
        # NOTE: 何もデータを持っていないので同じクラスであればTrue
        return True


class SchedulingInfo:
    """[17~20,37] スケジューリング情報 - 未実装"""
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SchedulingInfo):
            return False
        # NOTE: 何もデータを持っていないので同じクラスであればTrue
        return True

class MemoryAddressInfo:
    """
    メモリセグメントのアドレス情報 - 未実装
    このブロックの情報はカーネルバージョンによって位置が変わる可能性がある
    man proc(5) を確認する
    """
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryAddressInfo):
            return False
        # NOTE: 何もデータを持っていないので同じクラスであればTrue
        return True


# NOTE: まだ他にも情報があると思うが省く


class ProcessStat:
    """/proc/[pid]/stat を解析するクラス"""

    def __init__(self):
        self.basic: ProcessBasicInfo = ProcessBasicInfo()
        self.cpu_time: ProcessCpuTime = ProcessCpuTime()
        self.resource: ProcessResourceStat = ProcessResourceStat()

        self.page_fault: PageFaultInfo = PageFaultInfo()  # no supported
        self.scheduling: SchedulingInfo = SchedulingInfo()  # no supported
        self.memory_address: MemoryAddressInfo = MemoryAddressInfo()  # no supported
        # NOTE: 他にも情報があれば追加する

        # statファイルを読み込んだときのタイムスタンプ - time.time()
        self.timestamp: float = 0.0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessStat):
            return False
        print("ProcessStat.__eq__")
        return (
            self.basic == other.basic and
            self.cpu_time == other.cpu_time and
            self.resource == other.resource and
            # 空のデータオブジェクトだが比較は行う
            # これらはすべてTrueになる
            self.page_fault == other.page_fault and
            self.scheduling == other.scheduling and
            self.memory_address == other.memory_address
        )


class PidStatFile:
    """/proc/[pid]/stat を読み込むクラス"""

    @staticmethod
    def _parse(pid: int, data: str) -> Union[ProcessStat, None]:
        # コマンド名 (comm) はカッコ () で囲まれているため、特殊なパースが必要
        # 例: 123 (my process) R ...
        # 最初の開きカッコ '(' と最後の閉じカッコ ')' の位置を見つける
        first_paren_open = data.find("(")
        last_paren_close = data.rfind(")")
        if (
            first_paren_open == -1 or
            last_paren_close == -1 or
            first_paren_open >= last_paren_close
        ):
            print(
                f"Error parsing /proc/{pid}/stat format: Could not find command name in parens."
            )
            return None

        # フィールド1 (pid)
        pid_str = data[:first_paren_open].strip()
        try:
            pid_val = int(pid_str)
            if pid_val != pid:  # 一応整合性チェック
                print(
                    f"Warning: PID in stat file ({pid_val}) does not match requested PID ({pid})."
                )
        except ValueError:
            print(f"Error parsing PID from stat file: '{pid_str}'")
            return None

        # フィールド2 (command) - カッコ内のコマンド文字列
        command_str = data[first_paren_open + 1 : last_paren_close]

        # フィールド3以降 - 最後の閉じカッコの後の部分をスペースで分割
        remaining_fields_str = data[last_paren_close + 1 :].strip()
        stat_fields_after_command = remaining_fields_str.split()

        # man proc(5) のフィールド番号と stat_fields_after_command のインデックスの対応:
        # Field 3 (state)   -> stat_fields_after_command[0]
        # Field 4 (gid)    -> stat_fields_after_command[1]
        # ...
        # Field N           -> stat_fields_after_command[N - 3]
        try:
            # BasicProcessInfo (Fields 3-8)
            basic_info = ProcessBasicInfo()
            basic_info.pid = pid_val
            basic_info.command = command_str
            basic_info.state = stat_fields_after_command[0]  # 3
            basic_info.parent_pid = int(stat_fields_after_command[1])  # 4
            basic_info.gid = int(stat_fields_after_command[2])  # 5
            basic_info.session = int(stat_fields_after_command[3])  # 6
            basic_info.tty_device_num = int(stat_fields_after_command[4])  # 7
            basic_info.tty_gid = int(stat_fields_after_command[5])  # 8

            # PageFaultInfo (Fields 10-13) - no supported

            # ProcessCpuTimes (Fields 14-17)
            cpu_times = ProcessCpuTime()
            cpu_times.user = int(stat_fields_after_command[11])  # 14
            cpu_times.system = int(stat_fields_after_command[12])  # 15
            cpu_times.child_user = int(stat_fields_after_command[13])  # 16
            cpu_times.child_system = int(stat_fields_after_command[14])  # 17

            # SchedulingInfo (Fields 18-21, 38) - no supported

            # ResourceStats (Fields 22-25)
            # NOTE: Field 22 (starttime) は MemoryStats の一部として扱われることも多い
            # starttime はフィールド番号 22。stat_fields_after_comm のインデックスは 22 - 3 = 19
            resource_stats = ProcessResourceStat()
            resource_stats.start_time = int(stat_fields_after_command[19])  # 22
            resource_stats.virtual_size = int(stat_fields_after_command[20])  # 23
            resource_stats.rss = int(stat_fields_after_command[21])  # 24
            resource_stats.rss_limit = int(stat_fields_after_command[22])  # 25

            # MemoryAddressInfo (Fields 26-28, 45-52など) - no supported

            # 全てを ProcessStat オブジェクトにまとめる
            process_stat = ProcessStat()
            process_stat.basic = basic_info
            process_stat.cpu_time = cpu_times
            process_stat.resource = resource_stats
            process_stat.timestamp = time.time()
            return process_stat

        except (ValueError, IndexError) as e:
            print(f"Error parsing fields from /proc/{pid}/stat: {e}")
            print(f"Line content: {data}")
            # print(f"Fields after comm: {stat_fields_after_comm}") # デバッグ用
            return None
        except Exception as e:
            print(f"An unexpected error occurred during parsing: {e}")
            return None
        
    @staticmethod
    def _read_stat_file(pid: int) -> str:
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Process with PID {pid} not found.")
            return ""
        except Exception as e:
            print(f"Error reading /proc/{pid}/stat for PID {pid}: {e}")
            return ""

    @staticmethod
    def load(pid: int) -> Union[ProcessStat, None]:
        """
        指定したPIDの /proc/<pid>/stat ファイルを読み込み、ProcessStat オブジェクトとしてパースする。
        プロセスが存在しない、または読み込み・パースに失敗した場合は None を返す。
        """
        contents = PidStatFile._read_stat_file(pid)
        if contents == "":
            return None
        return PidStatFile._parse(pid, contents)


class SystemCpuTime:
    """
    /prc/statのCPU時間の統計(jiffies単位)
    """

    def __init__(self):
        self.user: int = 0  # ユーザーCPU時間
        self.nice: int = 0  # ユーザーCPU時間(優先度低)
        self.system: int = 0  # システムCPU時間
        self.idle: int = 0  # アイドルCPU時間
        self.iowait: int = 0 # I/O待ちCPU時間
        self.irq: int = 0 # 割り込みCPU時間
        self.softirq: int = 0 # ソフトウェア割り込みCPU時間
        self.steal: int = 0 # スティールCPU時間
        self.guest: int = 0 # ゲストCPU時間
        self.guest_nice: int = 0 # ゲストCPU時間(優先度低)

    @property
    def total(self) -> int:
        """合計CPU時間をjiffies単位で返す"""
        return sum(
            [
                self.user,
                self.nice,
                self.system,
                self.idle,
                self.iowait,
                self.irq,
                self.softirq,
                self.steal,
                self.guest,
                self.guest_nice,
            ]
        )

    @property
    def total_seconds(self) -> float:
        """合計CPU時間を秒単位で返す"""
        return self.total / CLOCK_TICKS_PER_SECOND

    @property
    def total_idle(self) -> int:
        """アイドルCPU時間をjiffies単位で返す"""
        return self.idle + self.iowait

    @property
    def total_busy(self) -> int:
        """非アイドルCPU時間をjiffies単位で返す"""
        return self.total - self.idle
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SystemCpuTime):
            return False
        return (
            self.user == other.user and
            self.nice == other.nice and
            self.system == other.system and
            self.idle == other.idle and
            self.iowait == other.iowait and
            self.irq == other.irq and
            self.softirq == other.softirq and
            self.steal == other.steal and
            self.guest == other.guest and
            self.guest_nice == other.guest_nice
        )


class SystemStat:
    """
    システム全体の情報を表すクラス
    """
    def __init__(self):
        self.cpu_time: SystemCpuTime = SystemCpuTime()
        self.processor_times: List[SystemCpuTime] = []
        # NOTE: 他にもあるが省略(割り込み回数、コンテキストスイッチの回数...)

        # statファイルを読み込んだときのタイムスタンプ(time.time())
        self.timestamp: float = 0.0
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SystemStat):
            return False
        return (
            self.cpu_time == other.cpu_time and
            self.processor_times == other.processor_times
        )


class SystemStatFile:
    """
    /proc/statファイルを読み込み・解析するクラス
    """

    @staticmethod
    def _read_lines() -> List[str]:
        try:
            with open("/proc/stat", "r") as f:
                return f.readlines()
        except FileNotFoundError:
            print("Error: /proc/stat not found.")
            return []

    @staticmethod
    def _set_cpu_times(parts: List[str]) -> SystemCpuTime:
        if len(parts) < 11:
            raise ValueError("Invalid /proc/stat format")
        time_stats = SystemCpuTime()
        time_stats.user = int(parts[1])
        time_stats.nice = int(parts[2])
        time_stats.system = int(parts[3])
        time_stats.idle = int(parts[4])
        time_stats.iowait = int(parts[5])
        time_stats.irq = int(parts[6])
        time_stats.softirq = int(parts[7])
        time_stats.steal = int(parts[8])
        time_stats.guest = int(parts[9])
        time_stats.guest_nice = int(parts[10])
        return time_stats

    @staticmethod
    def _parse(lines: List[str]) -> Union[SystemStat, None]:
        """/proc/stat を解析する"""

        total_processors: Union[SystemCpuTime, None] = None
        processors: list[SystemCpuTime] = []

        for line in lines:
            parts = line.split()
            # 空行はスキップ
            if not parts:
                continue

            keyword = parts[0]
            # 全CPU合計の行
            if keyword == "cpu":
                total_processors = SystemStatFile._set_cpu_times(parts)
            # 各CPUの行
            elif keyword.startswith("cpu"):
                cpu_stat = SystemStatFile._set_cpu_times(parts)
                processors.append(cpu_stat)
            # NOTE: その他の情報については省略
            else:
                pass
        if total_processors is None:
            print("Error: Could not find 'cpu' line in /proc/stat.")
            return None  # 全体合計の行がない場合は解析失敗とみなす

        system_stat = SystemStat()
        system_stat.cpu_time = total_processors
        system_stat.processor_times = processors
        system_stat.timestamp = time.time()
        # NOTE: 他にも情報があれば追加する
        return system_stat

    @staticmethod
    def load() -> Union[SystemStat, None]:
        """
        /proc/stat を読み込む/解析する
        失敗の場合はNoneを返す
        """
        lines = SystemStatFile._read_lines()
        if not lines:
            return None
        return SystemStatFile._parse(lines)


class MeasurementResult:
    def __init__(self):
        self.usage_percent = 0.0
        self.timestamp = 0.0

def measure_process_stat(pid: int, delay: float = 1.0) -> Union[MeasurementResult, None]:
    """
    指定したPIDのCPU使用率(%)を計測する
    """

    # --- 時点 t1 のデータを取得 ---
    process_stat1 = PidStatFile.load(pid)
    system_stat1 = SystemStatFile.load()
    if process_stat1 is None or system_stat1 is None:
        return None

    # ...
    time.sleep(delay)

    # --- 時点 t2 のデータを取得 ---
    process_stat2 = PidStatFile.load(pid)
    system_stat2 = SystemStatFile.load()
    if process_stat2 is None or system_stat2 is None:
        return None

    # --- CPU時間の変化量を計算(jiffies) ---
    proc_time_diff = (
        process_stat2.cpu_time.total_cpu_time - process_stat1.cpu_time.total_cpu_time
    )
    system_time_diff = system_stat2.cpu_time.total - system_stat1.cpu_time.total


    # --- CPU使用率を計算(%) ---
    result = MeasurementResult()
    # 変化量が0 -> CPU使用率0%
    if system_time_diff == 0:
        result.usage_percent = 0.0
    else:
        result.usage_percent = (proc_time_diff / system_time_diff) * 100
    result.timestamp = system_stat2.timestamp
    return result

def measure_cpu_usage_percent(delay: float = 1.0) -> Union[float, None]:
    # --- 時点 t1 のデータを取得 ---
    system_stat1 = SystemStatFile.load()
    if system_stat1 is None:
        return None
    
    # ...
    time.sleep(delay)

    # --- 時点 t2 のデータを取得 ---
    system_stat2 = SystemStatFile.load()
    if system_stat2 is None:
        return None
    
    total_time_diff = system_stat2.cpu_time.total - system_stat1.cpu_time.total

    busy_time_diff = system_stat2.cpu_time.total_busy - system_stat1.cpu_time.total_busy

    # --- CPU使用率を計算(%) ---
    # 変化量が0 -> CPU使用率0%
    if total_time_diff == 0:
        return 0.0
    return (busy_time_diff / total_time_diff) * 100

def measure_processor_usages_percent(delay: float = 1.0) -> Union[List[float], None]:
    # --- 時点 t1 のデータを取得 ---
    system_stat1 = SystemStatFile.load()
    if system_stat1 is None:
        return None
    
    # zzz
    time.sleep(delay)

    # --- 時点 t2 のデータを取得 ---
    system_stat2 = SystemStatFile.load()
    if system_stat2 is None:
        return None

    processor_usages = []
    for i in range(len(system_stat1.processor_times)):
        total_time_diff = system_stat2.processor_times[i].total - system_stat1.processor_times[i].total
        busy_time_diff = system_stat2.processor_times[i].total_busy - system_stat1.processor_times[i].total_busy

        # --- CPU使用率を計算(%) ---
        # 変化量が0 -> CPU使用率0%
        if total_time_diff == 0:
            processor_usages.append(0.0)
        else:
            processor_usages.append((busy_time_diff / total_time_diff) * 100)

    return processor_usages

def format_time(t: float) -> str:
    time_str = time.strftime("%H:%M:%S", time.localtime(t))
    decimal = int((t - int(t)) * 100)
    return f"{time_str}.{decimal:02d}"

def print_processor_header(num_processors: int):
    header_labels = [f"%Cpu{i:02d}" for i in range(num_processors)]

    header_line_formatted = " ".join(f"{label:^6s}" for label in header_labels)

    print(header_line_formatted)

def _print(s: str):
    print(s)

def print_header():
    time_str = format_time(time.time())
    formatted_header = "  ".join([time_str, "%CPU"])
    _print(formatted_header)

def define_argument_parser() -> argparse.ArgumentParser:
    """コマンドライン引数を定義する"""
    p = argparse.ArgumentParser(description="Measure CPU usage for a specific process.")
    p.add_argument("pid", type=int, help="The PID of the process to measure.")
    return p


if __name__ == "__main__":
    print("-" * 20)
    print("Process Stat Tool")
    print("-" * 20)

    parser = define_argument_parser()
    args = parser.parse_args()

    target_process_id = args.pid
    
    print_header()

    while True:
        result = measure_process_stat(target_process_id)
        if result is None:
            _print("Error reading process stat file.")
            break
        time_str = format_time(result.timestamp)
        _print("  ".join([time_str, format(result.usage_percent, ".1f")]))
