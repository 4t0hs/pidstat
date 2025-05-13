import time
import os
import argparse
import signal


CLOCK_TICKS_PER_SECOND = os.sysconf("SC_CLK_TCK")


def jiffies_to_seconds(jiffies):
    return jiffies / CLOCK_TICKS_PER_SECOND


class ProcessBasicInfo:
    """基本的なプロセス情報"""

    def __init__(self):
        self.pid: int = 0  # 1: プロセスID
        self.command: str = ""  # 2: コマンド名 (カッコ付き)
        self.state: str = ""  # 3: プロセス状態 (R, S, D, Z, T, etc.)
        self.parent_pid: int = 0  # 4: 親プロセスID
        self.gid: int = 0  # 5: プロセスグループID
        self.session: int = 0  # 6: セッションID
        self.tty_device_num: int  # 7: 制御端末のメジャー/マイナー番号
        self.tty_gid: int  # 8: 制御端末のフォアグラウンドプロセスグループID


class ProcessCpuTimes:
    """[13~16] プロセスCPU時間情報(jiffies単位)"""

    def __init__(self):
        self.user_time  # 13: ユーザーCPU時間
        self.system_time  # 14: システムCPU時間
        self.child_user_time  # 15: 子プロセスのユーザーCPU時間
        self.child_system_time  # 16: 子プロセスのシステムCPU時間

    @property
    def total_cpu_time(self) -> int:
        """合計CPU時間をjiffies単位で返す"""
        return self.user_time + self.system_time

    @property
    def total_cpu_time_seconds(self) -> float:
        """合計CPU時間を秒単位で返す"""
        return jiffies_to_seconds(self.total_cpu_time())


class ProcessResourceStats:
    """[21~24] プロセスの資源に関する情報"""

    def __init__(self):
        self.start_time: int = 0  # 21: システム起動後のプロセス開始時間 (jiffies)
        self.virtual_size: int = 0  # 22: 仮想メモリサイズ (バイト)
        self.rss_size: int = 0  # 23: 常駐セットサイズ (ページ数)
        self.rss_limit: int = 0  # 24: RSS制限 (バイト)

    @property
    def start_time_seconds(self) -> float:
        """プロセス開始時間を秒単位で返す"""
        return jiffies_to_seconds(self.start_time)


class PageFaultInfo:
    """[9~12] ベージフォールト関連情報 - 未実装"""

    pass


class SchedulingInfo:
    """[17~20,37] スケジューリング情報 - 未実装"""

    pass


class MemoryAddressInfo:
    """
    メモリセグメントのアドレス情報 - 未実装
    このブロックの情報はカーネルバージョンによって位置が変わる可能性がある
    man proc(5) を確認する
    """

    pass


# NOTE: まだ他にも情報があると思うが省く


class ProcessStat:
    """/proc/[pid]/stat を解析するクラス"""

    def __init__(self):
        self.basic: ProcessBasicInfo
        self.cpu_times: ProcessCpuTimes
        self.resource: ProcessResourceStats

        self.page_fault: PageFaultInfo  # no supported
        self.scheduling: SchedulingInfo  # no supported
        self.memory_address: MemoryAddressInfo  # no supported
        # NOTE: 他にも情報があれば追加する

        # statファイルを読み込んだときのタイムスタンプ - time.time()
        self.timestamp: float = 0.0


class PidStatFile:

    @staticmethod
    def _parse(pid: int, data: str) -> ProcessStat | None:
        # コマンド名 (comm) はカッコ () で囲まれているため、特殊なパースが必要
        # 例: 123 (my process) R ...
        # 最初の開きカッコ '(' と最後の閉じカッコ ')' の位置を見つける
        first_paren_open = data.find("(")
        last_paren_close = data.rfind(")")
        if (
            first_paren_open == -1
            or last_paren_close == -1
            or first_paren_open >= last_paren_close
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
            basic_info: ProcessBasicInfo = ProcessBasicInfo(pid_val)
            basic_info.command = command_str
            basic_info.state = stat_fields_after_command[0]  # 3
            basic_info.parent_pid = int(stat_fields_after_command[1])  # 4
            basic_info.gid = int(stat_fields_after_command[2])  # 5
            basic_info.session = int(stat_fields_after_command[3])  # 6
            basic_info.tty_device_num = int(stat_fields_after_command[4])  # 7
            basic_info.tty_gid = int(stat_fields_after_command[5])  # 8

            # PageFaultInfo (Fields 10-13) - no supported

            # ProcessCpuTimes (Fields 14-17)
            cpu_times = ProcessCpuTimes(
                user_time=int(stat_fields_after_command[11]),  # 14
                system_time=int(stat_fields_after_command[12]),  # 15
                child_user_time=int(stat_fields_after_command[13]),  # 16
                child_system_time=int(stat_fields_after_command[14]),  # 17
            )

            # SchedulingInfo (Fields 18-21, 38) - no supported

            # ResourceStats (Fields 22-25)
            # NOTE: Field 22 (starttime) は MemoryStats の一部として扱われることも多い
            # starttime はフィールド番号 22。stat_fields_after_comm のインデックスは 22 - 3 = 19
            resource_stats = ProcessResourceStats()
            resource_stats.start_time = int(stat_fields_after_command[19])  # 22
            resource_stats.virtual_size = int(stat_fields_after_command[20])  # 23
            resource_stats.rss_size = int(stat_fields_after_command[21])  # 24
            resource_stats.rss_limit = int(stat_fields_after_command[22])  # 25

            # MemoryAddressInfo (Fields 26-28, 45-52など) - no supported

            # 全てを ProcessStat オブジェクトにまとめる
            process_stat = ProcessStat()
            process_stat.basic = basic_info
            process_stat.cpu_times = cpu_times
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
    def load(pid: int) -> ProcessStat | None:
        """
        指定したPIDの /proc/<pid>/stat ファイルを読み込み、ProcessStat オブジェクトとしてパースする。
        プロセスが存在しない、または読み込み・パースに失敗した場合は None を返す。
        """
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                data = f.readline()
        except FileNotFoundError:
            print(f"Error: Process with PID {pid} not found.")
            return None
        except Exception as e:
            print(f"Error reading /proc/{pid}/stat for PID {pid}: {e}")
            return None
        return PidStatFile._parse(pid, data)


class CpuTimeStat:
    """
    /prc/statのCPU時間の統計(jiffies単位)
    """

    def __init__(self):
        self.user: int  # ユーザーCPU時間
        self.nice: int  # ユーザーCPU時間(優先度低)
        self.system: int  # システムCPU時間
        self.idle: int  # アイドルCPU時間
        self.iowait: int  # I/O待ちCPU時間
        self.irq: int  # 割り込みCPU時間
        self.softirq: int  # ソフトウェア割り込みCPU時間
        self.steal: int  # スティールCPU時間
        self.guest: int  # ゲストCPU時間
        self.guest_nice: int  # ゲストCPU時間(優先度低)

    @property
    def total(self) -> int:
        """合計CPU時間をjiffies単位で返す"""
        return sum(
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
        )

    @property
    def total_seconds(self) -> float:
        """合計CPU時間を秒単位で返す"""
        return self.total / 100

    @property
    def idle(self) -> int:
        """アイドルCPU時間をjiffies単位で返す"""
        return self.idle + self.iowait

    @property
    def busy(self) -> int:
        """非アイドルCPU時間をjiffies単位で返す"""
        return self.total - self.idle


class SystemStat:
    """
    システム全体の情報を表すクラス
    """

    def __init__(self):
        self.total_cpu_time: CpuTimeStat
        self.processor_times: list[CpuTimeStat]
        # NOTE: 他にもあるが省略(割り込み回数、コンテキストスイッチの回数...)

        # statファイルを読み込んだときのタイムスタンプ(time.time())
        self.timestamp: float = 0.0


class SystemStatFile:
    """
    /proc/statファイルを読み込み・解析するクラス
    """

    @staticmethod
    def _read_lines() -> list[str]:
        try:
            with open("/proc/stat", "r") as f:
                return f.readlines()
        except FileNotFoundError:
            print("Error: /proc/stat not found.")
            return []

    @staticmethod
    def _set_cpu_times(parts: list[str]) -> CpuTimeStat:
        return CpuTimeStat(
            user=int(parts[1]),
            nice=int(parts[2]),
            system=int(parts[3]),
            idle=int(parts[4]),
            iowait=int(parts[5]),
            irq=int(parts[6]),
            softirq=int(parts[7]),
            steal=int(parts[8]),
            guest=int(parts[9]),
            guest_nice=int(parts[10]),
        )

    @staticmethod
    def _parse(lines: list[str]) -> SystemStat | None:
        """/proc/stat を解析する"""

        total_processors: CpuTimeStat | None = None
        processors: list[CpuTimeStat] = []

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
        system_stat.total_cpu_time = total_processors
        system_stat.processor_times = processors
        system_stat.timestamp = time.time()
        # NOTE: 他にも情報があれば追加する
        return system_stat

    @staticmethod
    def load() -> SystemStat | None:
        """
        /proc/stat を読み込む/解析する
        失敗の場合はNoneを返す
        """
        lines = SystemStatFile._read_lines()
        if not lines:
            return None
        return SystemStatFile._parse(lines)


def measure_pid_cpu_usage_percent(pid: int, delay: float = 1.0) -> float | None:
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
        process_stat1.cpu_times.total_cpu_time - process_stat2.cpu_times.total_cpu_time
    )
    system_time_diff = system_stat2.total_cpu_time - system_stat1.total_cpu_time

    # --- CPU使用率を計算(%) ---
    # 変化量が0 -> CPU使用率0%
    if system_time_diff == 0:
        return 0.0
    return (proc_time_diff / system_time_diff) * 100


def define_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure CPU usage for a specific process."
    )
    parser.add_argument("pid", type=int, help="The PID of the process to measure.")
    return parser


# --- 使い方 ---
if __name__ == "__main__":
    print("-" * 20)
    print("Process Stat Tool")
    print("-" * 20)

    signal.signal(signal.SIGINT, sigint_handler)

    parser = define_argument_parser()
    args = parser.parse_args()
