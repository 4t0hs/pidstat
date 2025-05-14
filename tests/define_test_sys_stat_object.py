""" sys_stat_test_data.txtを読み込んだときの期待値を定義する """

from pidstat import SystemCpuTime, SystemStat


def get_expected_sys_stat() -> SystemStat:
    stat = SystemStat()

    # 合計のCPU時間
    stat.cpu_time.user = 64967
    stat.cpu_time.nice = 0
    stat.cpu_time.system = 13885
    stat.cpu_time.idle = 8240933
    stat.cpu_time.iowait = 1025
    stat.cpu_time.irq = 0
    stat.cpu_time.softirq = 4248
    stat.cpu_time.steal = 0
    stat.cpu_time.guest = 0
    stat.cpu_time.guest_nice = 0
    # Core 0
    p = SystemCpuTime()
    p.user = 2564
    p.nice = 0
    p.system = 893
    p.idle = 412169
    p.iowait = 80
    p.irq = 0
    p.softirq = 2110
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 1
    p = SystemCpuTime()
    p.user = 3679
    p.nice = 0
    p.system = 370
    p.idle = 412071
    p.iowait = 133
    p.irq = 0
    p.softirq = 128
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 2
    p = SystemCpuTime()
    p.user = 4171
    p.nice = 0
    p.system = 901
    p.idle = 410840
    p.iowait = 75
    p.irq = 0
    p.softirq = 45
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 3
    p = SystemCpuTime()
    p.user = 1290
    p.nice = 0
    p.system = 335
    p.idle = 414530
    p.iowait = 281
    p.irq = 0
    p.softirq = 27
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 4
    p = SystemCpuTime()
    p.user = 4447
    p.nice = 0
    p.system = 890
    p.idle = 410607
    p.iowait = 50
    p.irq = 0
    p.softirq = 16
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 5
    p = SystemCpuTime()
    p.user = 1470
    p.nice = 0
    p.system = 483
    p.idle = 414418
    p.iowait = 11
    p.irq = 0
    p.softirq = 14
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 6
    p = SystemCpuTime()
    p.user = 3653
    p.nice = 0
    p.system = 984
    p.idle = 411285
    p.iowait = 25
    p.irq = 0
    p.softirq = 15
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 7
    p = SystemCpuTime()
    p.user = 1520
    p.nice = 0
    p.system = 282
    p.idle = 414561
    p.iowait = 25
    p.irq = 0
    p.softirq = 9
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 8
    p = SystemCpuTime()
    p.user = 4241
    p.nice = 0
    p.system = 1038
    p.idle = 410620
    p.iowait = 37
    p.irq = 0
    p.softirq = 40
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 9
    p = SystemCpuTime()
    p.user = 1600
    p.nice = 0
    p.system = 367
    p.idle = 414440
    p.iowait = 22
    p.irq = 0
    p.softirq = 10
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 10
    p = SystemCpuTime()
    p.user = 3542
    p.nice = 0
    p.system = 914
    p.idle = 411607
    p.iowait = 38
    p.irq = 0
    p.softirq = 11
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 11
    p = SystemCpuTime()
    p.user = 1905
    p.nice = 0
    p.system = 382
    p.idle = 414081
    p.iowait = 13
    p.irq = 0
    p.softirq = 6
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 12
    p = SystemCpuTime()
    p.user = 4461
    p.nice = 0
    p.system = 867
    p.idle = 410668
    p.iowait = 31
    p.irq = 0
    p.softirq = 19
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 13
    p = SystemCpuTime()
    p.user = 6233
    p.nice = 0
    p.system = 1062
    p.idle = 408171
    p.iowait = 15
    p.irq = 0
    p.softirq = 400
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 14
    p = SystemCpuTime()
    p.user = 4287
    p.nice = 0
    p.system = 834
    p.idle = 410669
    p.iowait = 31
    p.irq = 0
    p.softirq = 171
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 15
    p = SystemCpuTime()
    p.user = 2822
    p.nice = 0
    p.system = 542
    p.idle = 412628
    p.iowait = 21
    p.irq = 0
    p.softirq = 154
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 16
    p = SystemCpuTime()
    p.user = 3716
    p.nice = 0
    p.system = 842
    p.idle = 411307
    p.iowait = 41
    p.irq = 0
    p.softirq = 171
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 17
    p = SystemCpuTime()
    p.user = 2790
    p.nice = 0
    p.system = 521
    p.idle = 412673
    p.iowait = 31
    p.irq = 0
    p.softirq = 192
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 18
    p = SystemCpuTime()
    p.user = 3852
    p.nice = 0
    p.system = 856
    p.idle = 410933
    p.iowait = 35
    p.irq = 0
    p.softirq = 396
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    # Core 19
    p = SystemCpuTime()
    p.user = 2724
    p.nice = 0
    p.system = 522
    p.idle = 412646
    p.iowait = 19
    p.irq = 0
    p.softirq = 314
    p.steal = 0
    p.guest = 0
    p.guest_nice = 0
    stat.processor_times.append(p)
    return stat
