from pytest_mock import MockerFixture
import os

from pidstat import PidStatFile
from pidstat import ProcessStat, ProcessBasicInfo, ProcessCpuTime, ProcessResourceStat, PageFaultInfo, SchedulingInfo, MemoryAddressInfo, SchedulingInfo, MemoryAddressInfo
from tests.define_test_proc_stat_object import get_expected_process_stat

def test_read_stat_file():
    pid = 1
    contents = PidStatFile._read_stat_file(pid)
    assert contents != ""

def test_read_non_existent_file():
    pid = -1
    contents = PidStatFile._read_stat_file(pid)
    assert contents == ""


def read_test_stat_file(pid: int) -> str:
    TEST_STAT_FILE = f"{os.path.dirname(__file__)}/pid1_stat_test_data.txt"
    with open(TEST_STAT_FILE, "r") as f:
        return f.read()
    
def read_non_existent_stat_file(pid: int) -> str:
    return ""
    
def test_parse_stat_file():
    pid = 1
    contents = read_test_stat_file(pid)

    assert contents != ""

    process_stat = PidStatFile._parse(pid, contents)

    assert process_stat is not None
    expected = get_expected_process_stat()

    assert process_stat == expected

def test_load_stat_file(mocker: MockerFixture):
    pid = 1
    mocker.patch.object(PidStatFile, "_read_stat_file", return_value=read_test_stat_file(1))
    process_stat = PidStatFile.load(pid)

    assert process_stat is not None
    expected = get_expected_process_stat()
    assert process_stat == expected

def test_load_non_existent_stat_file(mocker: MockerFixture):
    pid = 1
    mocker.patch.object(PidStatFile, "_read_stat_file", return_value="")
    process_stat = PidStatFile.load(pid)

    assert process_stat is None
