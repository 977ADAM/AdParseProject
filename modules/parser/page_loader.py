import logging
import time
from urllib.parse import urlparse
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.error_handler import ErrorHandler
from utils.url_validator import URLValidator
from config.settings import Settings

class PageLoader:
    """Класс для загрузки и управления веб-страницами с обработкой ошибок"""
    def __init__(self, driver: WebDriver, config: Settings):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validator = URLValidator()
        self.wait = WebDriverWait(driver, self.config.PAGE_LOAD_TIMEOUT)
        
    def load_page(self, url, retries=None) -> bool:
        """Загружает страницу с обработкой ошибок и повторными попытками"""
        if retries is None:
            retries = self.config.MAX_RETRIES
            
        if not self.validator.is_valid_url(url):
            self.logger.error(f"Неверный URL-адрес: {url}")
            return False
            
        for attempt in range(retries):
            try:
                self.logger.info(f"Загрузка страницы: {url} (попытка {attempt + 1}/{retries})")
                
                self.driver.get(url)
                
                if self._wait_for_page_loaded():
                    self.logger.info(f"Успешно загружено: {url}")
                    return True
                else:
                    self.logger.warning(f"Загрузка страницы не завершена: {url}")
                    
            except TimeoutException:
                self.logger.warning(f"Тайм-аут загрузки {url} (попытка {attempt + 1})")
                if attempt == retries - 1:
                    self.logger.error(f"Не удалось загрузить {url} после {retries} попытки")
                    return False
                    
            except WebDriverException as e:
                error_type = ErrorHandler.handle_driver_error(e)
                self.logger.warning(f"Ошибка веб-драйвера ({error_type}) загрузка {url}: {str(e)}")
                if attempt == retries - 1:
                    return False
                    
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка загрузки {url}: {str(e)}")
                if attempt == retries - 1:
                    return False
                    
            if attempt < retries - 1:
                time.sleep(self.config.RETRY_DELAY * (attempt + 1))
                
        return False
    
    def _wait_for_page_loaded(self, timeout=None) -> bool:
        """Ожидание полной загрузки страницы"""
        if timeout is None:
            timeout = self.config.PAGE_LOAD_TIMEOUT
            
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            return True
            
        except TimeoutException:
            self.logger.warning("Истекло время загрузки страницы — продолжаем с текущего состояния")
            return True
        except Exception as e:
            self.logger.warning(f"Ожидание загрузки страницы прервано: {str(e)}")
            return True
    
    def get_page_info(self):
        """
        Сбор основной информации о странице
        
        Returns:
            dict: Информация о странице
        """
        try:
            return {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'domain': urlparse(self.driver.current_url).netloc,
                'page_source_length': len(self.driver.page_source),
                'window_size': self.driver.get_window_size(),
                'cookies': len(self.driver.get_cookies())
            }
        except Exception as e:
            self.logger.error(f"Error getting page info: {str(e)}")
            return {}
    
    def scroll_page(self, scroll_pause_time=0.4) -> bool:
        """Прокрутка страницы для загрузки динамического контента"""
        try:            
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_steps = 15
            scroll_step = page_height / scroll_steps

            for i in range(scroll_steps):
                self.driver.execute_script(f"window.scrollTo(0, {scroll_step * (i + 1)});")
                time.sleep(scroll_pause_time)
        
            time.sleep(1)
        
            for i in range(scroll_steps, 0, -1):
                self.driver.execute_script(f"window.scrollTo(0, {scroll_step * i});")
                time.sleep(scroll_pause_time)
        
            self.driver.execute_script("window.scrollTo(0, 0);")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error scrolling page: {str(e)}")
            return False
    
    def take_screenshot(self, filename=None):
        """Создание скриншота текущей страницы"""
        try:
            if filename is None:
                timestamp = int(time.time())
                domain = urlparse(self.driver.current_url).netloc
                filename = f"{domain}_{timestamp}.png"
            
            screenshot_path = self.config.SCREENSHOT_DIR / filename
            self.driver.save_screenshot(str(screenshot_path))
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None