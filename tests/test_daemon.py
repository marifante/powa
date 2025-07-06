from asyncio.coroutines import inspect
import pytest
import signal
import logging

from unittest import mock
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

from powa.daemon import PowaDaemon, start_daemon, DAEMON_LOCK_FILE


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


DUMMY_CONFIG0 = {
    "power_domain": {
        "VBAT": {
            "polling_interval": 30.0,
        },
        "USB": {
            "polling_interval": 10.0,
        }
    }
}

DEFAULT_PID = 1234

#@pytest.fixture
#def mock_config_file(tmp_path):
#    """Fixture to create a dummy YAML config file and return its path."""
#    config_path = tmp_path / "config.yml"
#    config_path.write_text("dummy: config")
#    return str(config_path)


@pytest.fixture
def mock_daemon_pid():
    """Fixture to mock the PID of the daemon."""
    with patch("powa.daemon.os.getpid", return_value=DEFAULT_PID) as mock_getpid:
        yield mock_getpid


@pytest.fixture
def mock_pd_controller():
    """Fixture to mock the PDController."""
    with patch("powa.daemon.PDController", autospec=True) as MockPDController:
        yield MockPDController


@pytest.fixture
def mock_data_exporter():
    """Fixture to mock the DataExporter."""
    with patch("powa.daemon.DataExporter", autospec=True) as MockDataExporter:
        yield MockDataExporter

@pytest.fixture
def mock_yaml_config():
    """Fixture to mock the parse_yaml_file function."""
    with patch("powa.daemon.parse_yaml_file", return_value=DUMMY_CONFIG0) as mock_parse_yaml:
        yield mock_parse_yaml

@pytest.fixture
def mock_file_existst():
    """Fixture to mock the existence of the lock file."""
    with patch("powa.daemon.os.path.exists", return_value=True) as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_open_file():
    """Fixture to mock the open function for the lock file."""
    with patch("powa.daemon.open", mock_open(read_data=str(DEFAULT_PID))) as mock_open_file:
        yield mock_open_file

@pytest.fixture
def mock_remove_file():
    """Fixture to mock the removal of the lock file."""
    with patch("powa.daemon.os.remove") as mock_remove:
        yield mock_remove

@pytest.fixture
def mock_gather():
    """Fixture to mock asyncio.gather."""
    with patch("powa.daemon.asyncio.gather", new_callable=AsyncMock) as mock_gather:
        yield mock_gather

#@pytest.fixture(autouse=True)
#def patch_dependencies(monkeypatch):
#    """
#    Fixture to patch external dependencies of PowaDaemon for isolation:
#    - parse_yaml_file returns a dummy config
#    - PowerDomain is replaced with a dummy enum
#    - PDController and DataExporter have dummy .task attributes
#    - logger is mocked
#    """
#    monkeypatch.setattr("powa.daemon.parse_yaml_file", lambda path: {"dummy": "config"})
#    class DummyDomain:
#        VBAT = type("Enum", (), {"value": "VBAT"})
#        USB = type("Enum", (), {"value": "USB"})
#    monkeypatch.setattr("powa.daemon.PowerDomain", [DummyDomain.VBAT, DummyDomain.USB])
#    monkeypatch.setattr("powa.daemon.PDController", lambda **kwargs: mock.Mock(task=mock.Mock(done=lambda: False, cancel=mock.Mock())))
#    monkeypatch.setattr("powa.daemon.DataExporter", lambda *a, **k: mock.Mock(task=mock.Mock(done=lambda: False, cancel=mock.Mock())))
#    monkeypatch.setattr("powa.daemon.logger", mock.Mock())

#@pytest.mark.parametrize("lock_exists", [False, True])
#def test_create_lock_file(tmp_path, mock_config_file, lock_exists):
#    """
#    Test _create_lock_file:
#    - If the lock file does not exist, it should be created with the correct PID.
#    - If the lock file exists, FileExistsError should be raised.
#    """
#    lock_file = tmp_path / "daemon.lock"
#    with mock.patch("powa.daemon.DAEMON_LOCK_FILE", str(lock_file)):
#        daemon = PowaDaemon(mock_config_file)
#        daemon._lock_file = str(lock_file)
#        daemon._pid = 1234
#        if lock_exists:
#            lock_file.write_text("already running")
#            with pytest.raises(FileExistsError):
#daemon._create_lock_file()
#        else:
#            daemon._create_lock_file()
#            assert lock_file.exists()
#            assert lock_file.read_text() == "1234"

#@pytest.mark.parametrize("lock_exists", [True, False])
#def test_handle_sigterm(tmp_path, mock_config_file, lock_exists):
#    """
#    Test _handle_sigterm:
#    - If the lock file exists, it should be removed.
#    - If the lock file does not exist, nothing should be removed.
#    - All tasks should be cancelled if not already done.
#    """
#    lock_file = tmp_path / "daemon.lock"
#    with mock.patch("powa.daemon.DAEMON_LOCK_FILE", str(lock_file)):
#        daemon = PowaDaemon(mock_config_file)
#        daemon._lock_file = str(lock_file)
#        daemon._tasks = [mock.Mock(done=mock.Mock(return_value=False), cancel=mock.Mock())]
#        if lock_exists:
#            lock_file.write_text("pid")
#        daemon._handle_sigterm(signal.SIGTERM, None)
#        assert not lock_file.exists()
#
#@pytest.mark.asyncio
#@pytest.mark.parametrize("tasks_none", [False, True])
#async def test_start(tmp_path, mock_config_file, tasks_none):
#    """
#    Test start:
#    - If any task is None, asyncio.gather should be awaited.
#    - Otherwise, only _create_lock_file should be called.
#    """
#    lock_file = tmp_path / "daemon.lock"
#    with mock.patch("powa.daemon.DAEMON_LOCK_FILE", str(lock_file)):
#        daemon = PowaDaemon(mock_config_file)
#        daemon._lock_file = str(lock_file)
#        daemon._create_lock_file= mock.Mock()
#        if tasks_none:
#            daemon._tasks = [None]
#            with mock.patch("asyncio.gather", new_callable=mock.AsyncMock) as gather_mock:
#                await daemon.start()
#                gather_mock.assert_awaited_once()
#        else:
#            daemon._tasks = [mock.Mock()]
#            await daemon.start()
#            daemon._create_lock_file.assert_called_once()


#@pytest.mark.usefixtures("mock_daemon_pid", "mock_pd_controller", "mock_data_exporter")
#@patch("powa.daemon.parse_yaml_file", return_value=DUMMY_CONFIG0)
#@patch("powa.daemon.os.path.exists", return_value=False)  # daemon lock file does not exists
#@patch("powa.daemon.open", create=True, return_value=mock_open)  # mock open lock file
#@patch("powa.daemon.asyncio.gather", new_callable=AsyncMock)
#def test_daemon_all_good_lock_file_is_removed(mock_daemon_pid, mock_pd_controller, mock_data_exporter,
#                                              mock_yaml_config, mock_os_path_exists, mock_open_file,
#                                              mock_gather):
#    """
#    Test that the daemon lock file is removed when the tasks ends gracefully.
#    """
#    # Arrange: Set up all the mocks
#    mock_daemon_pid.return_value = 1234
#    mock_gather.return_value = ["mocked_result1", "mocked_result2"]
#
#    # Act: Call start daemon with a mock config file
#    start_daemon(config="dummy_config.yml")
#
#    # Assert: Check if the daemon was started correctly (with the lock file) and then it was removed
#    mock_gather.assert_awaited_once()
#    mock_daemon_pid.assert_called_once()
#    mock_open_file.assert_called_once_with(DAEMON_LOCK_FILE, 'w')

def test_daemon_all_good_lock_file_is_removed(mock_daemon_pid, mock_pd_controller, mock_data_exporter,
                                              mock_yaml_config, mock_gather,
                                              mock_file_existst, mock_remove_file, mock_open_file):
    """
    Test that the daemon lock file is removed when the tasks ends gracefully.
    """
    # Arrange: Set up all the mocks
    logger.debug("Setting up mocks for PowaDaemon test")
    mock_gather.return_value = ["mocked_result1", "mocked_result2"]

    # Act: Call start daemon with a mock config file
    start_daemon(config="dummy_config.yml")

    # Assert: Check if the daemon was started correctly (with the lock file) and then it was removed
    mock_daemon_pid.assert_called_once()
    mock_file_existst.assert_called_once_with(DAEMON_LOCK_FILE)
    mock_gather.assert_awaited_once()
    mock_remove_file.assert_called_once_with(DAEMON_LOCK_FILE)

