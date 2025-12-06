import pytest
from unittest.mock import MagicMock, patch
from config.settings import Settings


@pytest.fixture
def mock_config():
    """Фикстура для мока настроек"""
    config = MagicMock(spec=Settings)
    config.RETRY_DELAY = 1
    config.PAGE_LOAD_TIMEOUT = 3
    config.MAX_RETRIES = 3
    return config

@pytest.fixture
def mock_driver():
    """Фикстура для мока Selenium WebDriver"""
    driver = MagicMock()
    driver.get = MagicMock()
    driver.execute_script = MagicMock()
    return driver


@pytest.fixture
def mock_logger():
    """Фикстура для мока логгера"""
    with patch('logging.getLogger') as mock_get_logger:
        logger = MagicMock()
        logger.info = MagicMock()
        logger.warning = MagicMock()
        logger.error = MagicMock()
        logger.debug = MagicMock()
        mock_get_logger.return_value = logger
        yield logger