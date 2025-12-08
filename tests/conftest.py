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

    mock_element = MagicMock()
    mock_element.is_displayed = MagicMock(return_value=True)
    mock_element.size = {'width': 300, 'height': 250}
    mock_element.location = {'x': 100, 'y': 200}
    mock_element.get_attribute = MagicMock(side_effect=lambda attr: {
        'class': 'yandex_rtb_78654387654',
        'id': 'adfox_09876543',
        'src': '',
        'href': '',
        'onclick': ''
    }.get(attr, ''))

    driver.find_element = MagicMock(return_value=mock_element)
    driver.find_elements = MagicMock(return_value=[mock_element])

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

@pytest.fixture
def mock_web_element():
    """Фикстура для мока WebElement"""
    element = MagicMock()
    element.tag_name = "div"
    element.text = "Sample Ad Text"
    element.is_displayed = MagicMock(return_value=True)
    element.is_enabled = MagicMock(return_value=True)
    element.size = {'width': 300, 'height': 250}
    element.location = {'x': 100, 'y': 200}
    element.click = MagicMock()
    element.value_of_css_property = MagicMock(return_value="pointer")
    element.get_attribute = MagicMock(side_effect=lambda attr: {
        'class': 'ad-banner google-ad',
        'id': 'google_ad_123',
        'src': 'https://googleads.g.doubleclick.net/pagead/123',
        'href': 'https://example.com/utm_source=google&utm_medium=cpc',
        'onclick': 'googleAdClick()'
    }.get(attr, ''))
    element.screenshot = MagicMock()
    return element