from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from config.settings import Settings
from config.browser_config import BrowserConfig
from core.memory_manager import MemoryManager
from core.error_handler import ErrorHandler
import logging
import time

class DriverManager:
    def __init__(self, config: Settings):
        self.config = config
        self.driver = None
        self.memory_manager = MemoryManager(self.config.MEMORY_LIMIT_MB)
        self.logger = logging.getLogger(__name__)
        
    def create_driver(self, headless=None):
        try:
            if not self.memory_manager.check_memory():
                self.logger.warning("Приближается лимит памяти, ожидание очистки...")

            headless_mode = headless if headless is not None else self.config.HEADLESS
            options = BrowserConfig.get_chrome_options(self.config)
            self.driver = webdriver.Chrome(options=options)
            
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome WebDriver успешно создан")
            return self.driver
            
        except WebDriverException as e:
            self.logger.error(f"Не удалось создать Chrome WebDriver: {str(e)}")
            ErrorHandler.handle_driver_error(e)
            return None
    
    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("Chrome WebDriver успешно закрыт")
            except Exception as e:
                self.logger.error(f"Ошибка закрытия драйвера: {str(e)}")
    
    def __enter__(self):
        return self.create_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit_driver()