import pytest
import allure
from allure_commons.types import Severity

from selenium.common.exceptions import TimeoutException

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
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.unit
    def test_load_page_timeout(self, mock_driver, mock_config):
        """Тест загрузки страницы с таймаутом"""
        
        mock_driver.get.side_effect = TimeoutException()
        page_loader = PageLoader(mock_driver, mock_config)
        url = "https://example.com"
        
        
        result = page_loader.load_page(url, retries=1)
        
        
        assert result is False
        assert mock_driver.get.call_count == 1
