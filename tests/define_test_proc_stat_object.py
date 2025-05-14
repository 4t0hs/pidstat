from pidstat import ProcessStat


def get_expected_process_stat():
    """ test_pid1_statファイルの内容をProcessStatクラスに変換したものを返す """
    stat = ProcessStat()
    # basic info
    stat.basic.pid = 1
    stat.basic.command = "systemd"
    stat.basic.state = "S"
    stat.basic.parent_pid = 0
    stat.basic.gid = 1
    stat.basic.session = 1
    stat.basic.tty_device_num = 0
    stat.basic.tty_gid = -1
    # Cpu time
    stat.cpu_time.user = 80
    stat.cpu_time.system = 57
    stat.cpu_time.child_user = 951
    stat.cpu_time.child_system = 391
    # resource stat
    stat.resource.start_time = 92
    stat.resource.virtual_size = 22347776
    stat.resource.rss = 3227
    stat.resource.rss_limit = 18446744073709551615
    return stat
