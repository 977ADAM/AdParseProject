import logging
import time
from urllib.parse import urlparse, parse_qs
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from modules.screenshot.capturer import ScreenshotCapturer

class RedirectTracker:
    """Класс для отслеживания и анализа редиректов после клика"""
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.screenshot_capturer = ScreenshotCapturer(driver, config)
    
    def track_redirect(self, attempt_number, original_window, original_windows, original_url, timeout=15):
        """Отслеживание редиректов после клика"""
        try:
            redirect_info = {
                'original_url': original_url,
                'redirect_chain': [],
                'final_url': None,
                'redirect_type': None,
                'new_windows': [],
                'utm_parameters': {},
                'tracking_parameters': {},
                'redirect_duration': 0
            }
            
            start_time = time.time()
            
            self._wait_for_page_stability(timeout)
            
            current_url = self.driver.current_url
            current_windows = set(self.driver.window_handles)
            new_windows = current_windows - original_windows
            
            redirect_info['final_url'] = current_url
            redirect_info['redirect_duration'] = time.time() - start_time
            
            if new_windows:
                redirect_info['redirect_type'] = 'new_window'
                redirect_info['new_windows'] = list(new_windows)

                self._analyze_new_window(new_windows, redirect_info, attempt_number)

            elif current_url != original_url:
                redirect_info['redirect_type'] = 'same_window'
                redirect_info['redirect_chain'] = self._reconstruct_redirect_chain(original_url, current_url)
            else:
                redirect_info['redirect_type'] = 'no_redirect'
            
            # Анализ параметров URL
            self._analyze_url_parameters(current_url, redirect_info)
            
            return redirect_info
            
        except Exception as e:
            self.logger.error(f"Error tracking redirect: {str(e)}")
            return {
                'error': str(e),
                'original_url': original_url,
                'final_url': self.driver.current_url if 'driver' in locals() else None
            }
    
    def _wait_for_page_stability(self, timeout):
        """Ожидание стабилизации страницы после клика"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            time.sleep(2)
            
        except TimeoutException:
            self.logger.warning("Page load timeout during redirect tracking")
    
    def _analyze_new_window(self, new_windows, redirect_info, attempt_number):
        """Анализ нового окна/вкладки"""
        try:
            if not new_windows:
                return
            
            new_window = next(iter(new_windows))
            self.driver.switch_to.window(new_window)
            
            self._wait_for_page_stability(15)
            
            redirect_info['final_url'] = self.driver.current_url
            self._analyze_url_parameters(self.driver.current_url, redirect_info)

            after_screenshot = self.screenshot_capturer.capture_visible_area(
                f"after_interaction_{attempt_number}.png"
                )
            redirect_info['after_screenshot'] = after_screenshot
            
            original_window = [w for w in self.driver.window_handles if w not in new_windows][0]
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.logger.error(f"Error analyzing new window: {str(e)}")
    
    def _reconstruct_redirect_chain(self, start_url, end_url):
        """
        Реконструкция цепочки редиректов (эмуляция)
        
        Note: В реальных условиях требуется более сложное отслеживание
        """
        chain = [start_url]
        
        # Здесь можно добавить логику анализа истории браузера
        # или использование proxy для отслеживания редиректов
        
        if end_url != start_url:
            chain.append(end_url)
        
        return chain
    
    def _analyze_url_parameters(self, url, redirect_info):
        """Анализ параметров URL на наличие UTM и tracking параметров"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0] if value else ''
            
            redirect_info['utm_parameters'] = utm_params
            
            tracking_keys = ['gclid', 'fbclid', 'msclkid', 'trk', 'tracking', 'ref', 'source']
            tracking_params = {}
            
            for key, value in query_params.items():
                if any(track_key in key.lower() for track_key in tracking_keys):
                    tracking_params[key] = value[0] if value else ''
            
            redirect_info['tracking_parameters'] = tracking_params
            
            redirect_info['parameter_analysis'] = {
                'total_parameters': len(query_params),
                'utm_count': len(utm_params),
                'tracking_count': len(tracking_params),
                'has_tracking': len(utm_params) > 0 or len(tracking_params) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing URL parameters: {str(e)}")