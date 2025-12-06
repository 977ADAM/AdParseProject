import pytest
from unittest.mock import patch
import allure
from allure_commons.types import Severity
from selenium.common.exceptions import TimeoutException, WebDriverException
from modules.parser.page_loader import PageLoader

@allure.epic("Parser Module")
@allure.feature("Page Loader")
class TestPageLoader:
    
    @allure.title("Test successful page load")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.unit
    def test_load_page_success(self, mock_driver, mock_config, mock_logger):
        """Тест успешной загрузки страницы"""
        
        page_loader = PageLoader(mock_driver, mock_config)
        url = "https://example.com"
        
        result = page_loader.load_page(url)
        
        assert result is True
        mock_driver.get.assert_called_once_with(url)
        mock_logger.info.assert_any_call(f"Успешно загружено: {url}")
    

    @allure.title("Test page load with timeout")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.unit
    def test_load_page_timeout(self, mock_driver, mock_config):
        """Тест загрузки страницы с таймаутом"""
        
        mock_driver.get.side_effect = TimeoutException()
        page_loader = PageLoader(mock_driver, mock_config)
        url = "https://example.com"
        
        
        result = page_loader.load_page(url, retries=2)
        
        
        assert result is False
        assert mock_driver.get.call_count == 2

    @allure.title("Test page load with retries")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.unit
    @pytest.mark.flaky(reruns=3, reruns_delay=1)
    def test_load_page_with_retries(self, mock_driver, mock_config):
        """Тест загрузки страницы с повторными попытками"""
        
        mock_driver.get.side_effect = [
            WebDriverException(),
            None
        ]
        page_loader = PageLoader(mock_driver, mock_config)
        url = "https://example.com"
        
        
        with patch.object(page_loader, '_wait_for_page_loaded', return_value=True):
            result = page_loader.load_page(url, retries=2)
        
        
        assert result is True
        assert mock_driver.get.call_count == 2

    @allure.title("Test invalid URL handling")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.unit
    @pytest.mark.parametrize("url, expected", [
        ("not-a-url", False),
        ("", False),
        (None, False),
        ("https://valid-url.com", True)
    ])
    def test_load_page_invalid_url(self, mock_driver, mock_config, url, expected):
        """Тест обработки невалидных URL"""
        
        page_loader = PageLoader(mock_driver, mock_config)
        
        result = page_loader.load_page(url)

        assert result == expected

    @allure.title("Test page scrolling")
    @allure.severity(Severity.MINOR)
    @pytest.mark.unit
    def test_scroll_page(self, mock_driver, mock_config):
        """Тест прокрутки страницы"""
        
        mock_driver.execute_script.return_value  = 2000
        page_loader = PageLoader(mock_driver, mock_config)
        
        
        result = page_loader.scroll_page(scroll_steps=2, scroll_pause_time=0.1)
        
        assert result is True
        assert mock_driver.execute_script.call_count >= 6
