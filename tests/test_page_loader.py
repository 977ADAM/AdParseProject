"""
Тесты для модуля загрузки страниц.
"""

import pytest
from config.settings import Settings
from core.driver_manager import DriverManager
from modules.parser.page_loader import PageLoader


@pytest.mark.selenium
@pytest.mark.slow
@pytest.mark.integration
class TestPageLoader:
    """Тесты для PageLoader"""
    
    @pytest.fixture
    def driver_setup(self):
        """Фикстура для настройки драйвера и загрузчика"""
        config = Settings()
        config.HEADLESS = True
        config.PAGE_LOAD_TIMEOUT = 15
        
        driver_manager = DriverManager(config)
        driver = driver_manager.create_driver()
        
        page_loader = PageLoader(driver, config)
        
        yield driver, page_loader, driver_manager
        
        driver_manager.quit_driver()
    
    def test_load_valid_page(self, driver_setup):
        """Тест загрузки валидной страницы"""
        driver, page_loader, _ = driver_setup
        
        # Загружаем тестовую страницу
        result = page_loader.load_page("https://httpbin.org/html")
        
        assert result == True, "Страница должна загрузиться успешно"
        assert "Herman" in driver.page_source, "Страница должна содержать ожидаемый контент"
    
    def test_load_invalid_page(self, driver_setup):
        """Тест загрузки несуществующей страницы"""
        driver, page_loader, _ = driver_setup
        
        # Пытаемся загрузить несуществующую страницу
        result = page_loader.load_page("https://httpbin.org/status/404")
        
        # Страница загрузится, но вернет 404
        assert result == True, "Страница должна загрузиться (даже с 404)"
    
    def test_get_page_info(self, driver_setup):
        """Тест получения информации о странице"""
        driver, page_loader, _ = driver_setup
        
        page_loader.load_page("https://httpbin.org/html")
        page_info = page_loader.get_page_info()
        
        # Проверяем ключевые поля
        assert 'url' in page_info
        assert 'title' in page_info
        assert 'domain' in page_info
        assert 'page_source_length' in page_info
        
        assert 'httpbin.org' in page_info['domain']
        assert page_info['page_source_length'] > 0
    
    def test_scroll_page(self, driver_setup):
        """Тест прокрутки страницы"""
        driver, page_loader, _ = driver_setup
        
        # Загружаем длинную страницу
        page_loader.load_page("https://httpbin.org/bytes/10000")
        
        # Прокручиваем
        result = page_loader.scroll_page(scroll_pause_time=0.5)
        
        assert result == True, "Прокрутка должна завершиться успешно"
    
    @pytest.mark.parametrize("url, expected_in_title", [
        ("https://httpbin.org/html", "Herman")
    ])
    def test_multiple_pages(self, driver_setup, url, expected_in_title):
        """Параметризованный тест для нескольких страниц"""
        driver, page_loader, _ = driver_setup
        
        result = page_loader.load_page(url)
        assert result == True
        
        page_content = driver.page_source
        assert expected_in_title in page_content