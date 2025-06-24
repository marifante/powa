import pytest
import signal

from unittest import mock

from powa.daemon import PowaDaemon


@pytest.fixture
def mock_config_file(tmp_path):
    """Fixture to create a dummy YAML config file and return its path."""
    config_path = tmp_path / "config.yml"
    config_path.write_text("dummy: config")
    return str(config_path)


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

@pytest.mark.parametrize("lock_exists", [False, True])
def test_create_lock_file(tmp_path, mock_config_file, lock_exists):
    """
    Test _create_lock_file:
    - If the lock file does not exist, it should be created with the correct PID.
    - If the lock file exists, FileExistsError should be raised.
    """
    lock_file = tmp_path / "daemon.lock"
    with mock.patch("powa.daemon.DAEMON_LOCK_FILE", str(lock_file)):
        daemon = PowaDaemon(mock_config_file)
        daemon._lock_file = str(lock_file)
        daemon._pid = 1234
        if lock_exists:
            lock_file.write_text("already running")
            with pytest.raises(FileExistsError):
                daemon._create_lock_file()
        else:
            daemon._create_lock_file()
            assert lock_file.exists()
            assert lock_file.read_text() == "1234"

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
#        daemon._create_lock_file = mock.Mock()
#        if tasks_none:
#            daemon._tasks = [None]
#            with mock.patch("asyncio.gather", new_callable=mock.AsyncMock) as gather_mock:
#                await daemon.start()
#                gather_mock.assert_awaited_once()
#        else:
#            daemon._tasks = [mock.Mock()]
#            await daemon.start()
#            daemon._create_lock_file.assert_called_once()
#`
