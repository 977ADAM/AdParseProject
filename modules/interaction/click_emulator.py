import logging
import time
import random
from selenium.common.exceptions import (
    ElementClickInterceptedException, 
    StaleElementReferenceException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.error_handler import ErrorHandler
from config.settings import Settings

class ClickEmulator:
    """Класс для эмуляции реалистичного взаимодействия с рекламными элементами"""
    def __init__(self, driver, config: Settings):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()
        self.wait = WebDriverWait(driver, config.PAGE_LOAD_TIMEOUT)
    
    def analyze_clickability(self, ad_element):
        """Анализ возможности клика по рекламному элементу"""
        try:
            analysis = {
                'is_clickable': False,
                'click_method': None,
                'reason': '',
                'element_info': self._get_element_click_info(ad_element)
            }
            
            
            if not ad_element.is_displayed():
                analysis['reason'] = 'Element not visible'
                return analysis
            
            if not ad_element.is_enabled():
                analysis['reason'] = 'Element not enabled'
                return analysis
            
            click_methods = [
                self._try_direct_click,
                self._try_javascript_click,
                self._try_action_chain_click,
                # self._try_force_click
            ]

            original_window = self.driver.current_window_handle
            original_windows = self.driver.window_handles
            
            for method in click_methods:
                method_name = method.__name__
                self.logger.debug(f"Trying click method: {method_name}")
                
                result = method(ad_element)

                self._restore_original_state(original_window, original_windows)

                if result['success']:
                    analysis['is_clickable'] = True
                    analysis['click_method'] = method_name
                    analysis['reason'] = 'Success'
                    analysis['click_details'] = result
                    break
                else:
                    analysis['reason'] = result.get('error', 'Unknown error')
            
            return analysis
            
        except Exception as e:
            error_type = self.error_handler.handle_element_error(e, "clickability analysis")
            self.logger.error(f"Error analyzing clickability: {str(e)}")
            return {
                'is_clickable': False,
                'click_method': None,
                'reason': f'Analysis error: {error_type}',
                'error': str(e)
            }
    
    def _try_direct_click(self, element):
        """Попытка прямого клика"""
        try:
            element.click()
            return {'success': True, 'method': 'direct_click'}
        except ElementClickInterceptedException:
            return {'success': False, 'error': 'Element intercepted'}
        except Exception as e:
            return {'success': False, 'error': f'Direct click failed: {str(e)}'}
    
    def _try_javascript_click(self, element):
        """Попытка клика через JavaScript"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return {'success': True, 'method': 'javascript_click'}
        except Exception as e:
            return {'success': False, 'error': f'JS click failed: {str(e)}'}
    
    def _try_action_chain_click(self, element):
        """Попытка клика через ActionChains"""
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            return {'success': True, 'method': 'action_chain_click'}
        except Exception as e:
            return {'success': False, 'error': f'Action chain click failed: {str(e)}'}
    
    def _try_force_click(self, element):
        """Принудительный клик через JS с обработкой перехвата"""
        try:
            # Сначала скроллим к элементу
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # Убираем возможные перекрывающие элементы
            self.driver.execute_script("""
                var element = arguments[0];
                var parent = element;
                while (parent) {
                    if (parent.style && parent.style.zIndex === '9999') {
                        parent.style.zIndex = 'auto';
                    }
                    parent = parent.parentElement;
                }
            """, element)
            
            # Клик через JS
            self.driver.execute_script("arguments[0].click();", element)
            return {'success': True, 'method': 'force_click'}
        except Exception as e:
            return {'success': False, 'error': f'Force click failed: {str(e)}'}
    



    def _get_element_click_info(self, element):
        """Получение детальной информации об элементе для клика"""
        try:
            return {
                'tag_name': element.tag_name,
                'location': element.location,
                'size': element.size,
                'is_displayed': element.is_displayed(),
                'is_enabled': element.is_enabled(),
                'cursor_style': element.value_of_css_property('cursor'),
                'pointer_events': element.value_of_css_property('pointer-events'),
                'z_index': element.value_of_css_property('z-index'),
                'position': element.value_of_css_property('position'),
                'has_onclick': bool(element.get_attribute('onclick')),
                'href': element.get_attribute('href'),
                'target': element.get_attribute('target')
            }
        except Exception as e:
            self.logger.debug(f"Error getting element click info: {str(e)}")
            return {}
    



    def emulate_human_click(self, element, click_delay=1):
        """Эмуляция человеческого клика с реалистичными задержками"""
        try:
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            original_windows = set(self.driver.window_handles)
            
            self._prepare_for_click(element, click_delay)
            
            click_result = self._execute_human_click(element)
            
            if not click_result['success']:
                return click_result
            
            analysis_result = self._analyze_click_result(
                original_window, original_windows, original_url
            )
            
            return {
                'success': True,
                'click_method': click_result['method'],
                'result_analysis': analysis_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in human click emulation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    




    def _prepare_for_click(self, element, delay):
        """Подготовка к реалистичному клику"""
        time.sleep(delay * random.uniform(0.8, 1.2))
        
        self.driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center'
            });
        """, element)
        
        time.sleep(0.3)
        
        self._emulate_mouse_movement(element)
    
    def _emulate_mouse_movement(self, element):
        """Эмуляция движения мыши перед кликом"""
        try:
            actions = ActionChains(self.driver)
            
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
            
        except Exception as e:
            self.logger.debug(f"Mouse movement emulation failed: {str(e)}")
    




    def _execute_human_click(self, element):
        """Выполнение реалистичного клика"""
        try:
            methods = [
                self._human_direct_click,
                self._human_action_chain_click
            ]
            
            method = random.choice(methods)
            return method(element)
            
        except Exception as e:
            return {'success': False, 'error': f'Human click failed: {str(e)}'}
    





    def _human_direct_click(self, element):
        """Прямой клик с человеческой задержкой"""
        try:
            time.sleep(random.uniform(0.1, 0.3))
            element.click()
            return {'success': True, 'method': 'human_direct_click'}
        except Exception as e:
            return {'success': False, 'error': f'Human direct click failed: {str(e)}'}
    
    def _human_action_chain_click(self, element):
        """Клик через ActionChains с человеческими паузами"""
        try:
            actions = ActionChains(self.driver)
            
            actions.move_to_element(element)
            actions.pause(random.uniform(0.05, 0.15))
            actions.click()
            actions.pause(random.uniform(0.05, 0.15))
            actions.perform()
            
            return {'success': True, 'method': 'human_action_chain_click'}
        except Exception as e:
            return {'success': False, 'error': f'Human action chain click failed: {str(e)}'}
    






    def _analyze_click_result(self, original_window, original_windows, original_url):
        """Анализ результата клика"""
        try:
            result = {
                'new_window_opened': False,
                'url_changed': False,
                'redirect_occurred': False,
                'new_window_handle': None,
                'final_url': self.driver.current_url,
                'windows_count_change': len(self.driver.window_handles) - len(original_windows)
            }
            
            current_windows = set(self.driver.window_handles)
            new_windows = current_windows - original_windows
            
            if new_windows:
                result['new_window_opened'] = True
                result['new_window_handle'] = next(iter(new_windows)) if new_windows else None
            
            if self.driver.current_url != original_url:
                result['url_changed'] = True
                result['redirect_occurred'] = self._check_redirect_chain(original_url)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing click result: {str(e)}")
            return {'analysis_error': str(e)}
    
    def _check_redirect_chain(self, original_url):
        """Проверка наличия цепочки редиректов"""
        try:
            # Можно расширить для отслеживания цепочки редиректов
            return True  # Упрощенная проверка
        except:
            return False
        
    def _restore_original_state(self, original_window, original_windows):
        """Восстановление исходного состояния браузера"""
        try:
            current_windows = set(self.driver.window_handles)
            new_windows = current_windows - original_windows
            
            for window in new_windows:
                try:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                except:
                    pass
            
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.logger.warning(f"Error restoring original state: {str(e)}")