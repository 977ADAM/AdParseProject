"""
Простой тест для менеджера драйвера.
Этот тест проверяет базовую функциональность создания драйвера.
"""
import pytest


from config.settings import Settings
from core.driver_manager import DriverManager


class TestDriverManager:
    """Тесты для DriverManager"""
    
    @pytest.fixture
    def config(self):
        """Фикстура с конфигурацией для тестов"""
        config = Settings()
        config.HEADLESS = True  # Всегда в headless режиме для тестов
        config.PAGE_LOAD_TIMEOUT = 15  # Уменьшаем таймаут для тестов
        return config
    
    @pytest.mark.selenium
    @pytest.mark.slow
    def test_driver_creation(self, config):
        """Тест создания драйвера Chrome"""
        driver_manager = DriverManager(config)
        
        try:
            # Создаем драйвер
            driver = driver_manager.create_driver()
            
            # Проверяем, что драйвер создан
            assert driver is not None, "Драйвер должен быть создан"
            
            # Проверяем, что это Chrome
            assert "chrome" in driver.name.lower(), f"Ожидается Chrome, получен: {driver.name}"
            
            # Простой тест - открываем страницу
            driver.get("https://ria.ru/")
            
            # Проверяем заголовок
            assert "РИА Новости - события в Москве, России и мире сегодня: темы дня, фото, видео, инфографика, радио" in driver.title
            
            # Проверяем текущий URL
            assert "https://ria.ru/" in driver.current_url
            
        finally:
            # Всегда закрываем драйвер
            if 'driver' in locals():
                driver_manager.quit_driver()
    
    @pytest.mark.selenium
    @pytest.mark.slow
    def test_driver_context_manager(self, config):
        """Тест работы контекстного менеджера"""
        driver_manager = DriverManager(config)
        
        # Используем контекстный менеджер
        with driver_manager as driver:
            assert driver is not None, "Драйвер должен быть создан в контексте"
            
            # Простой тест
            driver.get("https://ria.ru/")
            assert driver.current_url is not None
        
        # После выхода из контекста драйвер должен быть закрыт
        assert driver_manager.driver is None, "Драйвер должен быть закрыт после контекста"
    
    @pytest.mark.selenium
    @pytest.mark.slow
    def test_driver_restart(self, config):
        """Тест перезапуска драйвера"""
        driver_manager = DriverManager(config)
        
        try:
            # Создаем первый драйвер
            driver1 = driver_manager.create_driver()
            driver_id1 = id(driver1)
            
            # Перезапускаем
            driver2 = driver_manager.restart_driver()
            driver_id2 = id(driver2)
            
            # Проверяем, что это разные объекты
            assert driver_id1 != driver_id2, "После перезапуска должен быть новый драйвер"
            
            # Проверяем, что новый драйвер работает
            driver2.get("https://ria.ru/")
            assert "РИА Новости - события в Москве, России и мире сегодня: темы дня, фото, видео, инфографика, радио" in driver2.title
            
        finally:
            driver_manager.quit_driver()