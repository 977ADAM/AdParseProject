import logging
import time
from pathlib import Path
from config.settings import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from PIL import Image
import io

class ScreenshotCapturer:
    """Класс для захвата скриншотов веб-страниц"""
    def __init__(self, driver: WebDriver, config: Settings):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def capture_visible_area(self, filename=None):
        """Захват видимой области страницы"""
        try:
            if filename is None:
                filename = self._generate_filename("visible")
            
            screenshot_path = self.config.SCREENSHOT_DIR / filename
            
            self.driver.save_screenshot(str(screenshot_path))
            
            self.logger.info(f"Visible area screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Error capturing visible area: {str(e)}")
            return None
    
    def capture_full_page(self, filename=None):
        """Захват полной страницы (с прокруткой)"""
        try:
            if filename is None:
                filename = self._generate_filename("fullpage")
            
            screenshot_path = self.config.SCREENSHOT_DIR / filename
            
            total_width = self.driver.execute_script("return document.body.scrollWidth")
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            
            self.driver.set_window_size(self.config.WIDTH_WINDOW, total_height+100)
            
            self.driver.save_screenshot(str(screenshot_path))

            self.driver.set_window_size(self.config.WIDTH_WINDOW,self.config.HEIGHT_WINDOW)
            
            self.logger.info(f"Полный скриншот страницы сохранен: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Error capturing full page: {str(e)}")
            # Fallback to visible area
            return self.capture_visible_area(filename)
    
    def capture_element_screenshot(self, element, filename=None):
        """Захват скриншота конкретного элемента"""
        try:
            if filename is None:
                filename = self._generate_filename("element")
            
            screenshot_path = self.config.SCREENSHOT_DIR / filename
            
            element.screenshot(str(screenshot_path))
            
            self.logger.info(f"Element screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Error capturing element: {str(e)}")
            return None
    
    def capture_ads_screenshots(self, ads_data, base_filename=None):
        """Захват отдельных скриншотов для каждого рекламного блока"""
        screenshots = {}

        try:
            overlaying_element = self.driver.find_element(By.CSS_SELECTOR, "div.widgets__b-slide")
            self.driver.execute_script("arguments[0].style.visibility='hidden'", overlaying_element)
        except Exception:
            self.logger.info("Нижний виджет отсутствует")
        
        for i, ad in enumerate(ads_data, start=1):
            try:
                element = ad.get('element')
                if not element:
                    continue
                
                if base_filename:
                    filename = f"{base_filename}_ad_{i}.png"
                else:
                    filename = self._generate_filename(f"ad_{i}")
                
                screenshot_path = self.capture_element_screenshot(element, filename)
                if screenshot_path:
                    screenshots[f"ad_{i}"] = {
                        'path': screenshot_path,
                        'ad_data': ad
                    }
                    
            except Exception as e:
                self.logger.error(f"Error capturing ad screenshot {i+1}: {str(e)}")
                continue
        
        return screenshots
    
    def _generate_filename(self, prefix):
        """Генерация имени файла с timestamp"""
        timestamp = int(time.time())
        domain = self._get_safe_domain()
        return f"{domain}_{prefix}_{timestamp}.png"
    
    def _get_safe_domain(self):
        """Получение безопасного имени домена для файла"""
        try:
            domain = self.driver.current_url.split('//')[-1].split('/')[0]
            # Замена недопустимых символов
            domain = "".join(c for c in domain if c.isalnum() or c in ('-', '.'))
            return domain[:50]  # Ограничение длины
        except:
            return "page"