import pytest
from pytest_mock import MockerFixture
import os

from pidstat import SystemStatFile
from pidstat import SystemStat, SystemCpuTime
from tests.define_test_sys_stat_object import get_expected_sys_stat

def read_test_file():
    TEST_STAT_FILE = f"{os.path.dirname(__file__)}/sys_stat_test_data.txt"
    with open(TEST_STAT_FILE, "r") as f:
        return f.read()

def test_read_lines(mocker: MockerFixture):
    lines = SystemStatFile._read_lines()
    assert len(lines) > 0

def test_set_cpu_times(mocker: MockerFixture):
    parts = ["cpu", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    time_stats = SystemStatFile._set_cpu_times(parts)
    assert time_stats.user == 1
    assert time_stats.nice == 2
    assert time_stats.system == 3
    assert time_stats.idle == 4
    assert time_stats.iowait == 5
    assert time_stats.irq == 6
    assert time_stats.softirq == 7
    assert time_stats.steal == 8
    assert time_stats.guest == 9
    assert time_stats.guest_nice == 10

def test_set_cpu_times_invalid(mocker: MockerFixture):
    parts = ["cpu", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    with pytest.raises(ValueError):
        SystemStatFile._set_cpu_times(parts)

def test_parse(mocker: MockerFixture):
    lines = read_test_file().splitlines()
    system_stat = SystemStatFile._parse(lines)
    assert system_stat is not None
    expected = get_expected_sys_stat()
    assert system_stat.cpu_time == expected.cpu_time
    assert len(system_stat.processor_times) == len(expected.processor_times)
    assert system_stat.processor_times == expected.processor_times
    assert system_stat == expected

def test_load_file(mocker: MockerFixture):
    system_stat = SystemStatFile.load()
    assert system_stat is not None

def test_load_file_invalid(mocker: MockerFixture):
    mocker.patch.object(SystemStatFile, "_read_lines", return_value=None)
    system_stat = SystemStatFile.load()
    assert system_stat is None


