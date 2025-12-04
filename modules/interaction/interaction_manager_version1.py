import logging
import time
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

class InteractionManager:
    """Главный класс для управления всем процессом взаимодействия с рекламой"""
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 15)

    def perform_complete_ad_interaction(self, ads):
        """Выполнение полного цикла взаимодействия с рекламным блоком"""
        results = []

        self.logger.info("Начинаем клики по рекламным элементам")

        original_window = self.driver.current_window_handle
        self.logger.info(f"Оригинальная страница: {original_window}")

        for i, ad in enumerate(ads, start=1):
            try:
                element = ad.get('element')
                if not element:
                    continue

                self.logger.info(f"Клик по {i} элементу")

                result_interaction = self._interaction_proces(element)

                result = {
                    'ad_data': ad,
                    'interaction': result_interaction
                }

                results.append(result)

                if result_interaction.get('interaction_result', {}).get('success'):
                    original_window = result_interaction['interaction_result'].get('original_window')
                    if original_window:
                        self.restore_original_state(original_window)

            except Exception as e:
                self.logger.error(f"Ошибка клика по элементу {i}: {str(e)}")

        return results

    def _interaction_proces(self, element):
        """Процесс взаимодейстивия с одним блоком"""
        try:
            results = {
                'element_info': self._get_element_info(element),
                'click_analysis': self._analyze_clickability(element),
                'redirect_analysis': None,
                'interaction_result': None,
                'error': None
            }
            
            if results['click_analysis']['is_clickable']:
                click_result = self._click_element(element)
                results['interaction_result'] = click_result
                
                if click_result.get('success'):
                    results['redirect_analysis'] = self._analyze_redirect(
                        click_result.get('original_url'),
                        click_result.get('original_windows')
                    )
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error analyzing ad element: {str(e)}")

    def _get_element_info(self, element):
        """Получение базовой информации об элементе"""
        try:
            return {
                'tag_name': element.tag_name,
                'location': element.location,
                'size': element.size,
                'is_displayed': element.is_displayed(),
                'is_enabled': element.is_enabled(),
                'href': element.get_attribute('href'),
                'src': element.get_attribute('src'),
                'class': element.get_attribute('class'),
                'id': element.get_attribute('id'),
                'aria_label': element.get_attribute('aria-label'),
                'title': element.get_attribute('title')
            }
        except:
            return {}

    def _analyze_clickability(self, element):
        """Анализ кликабельности элемента"""
        try:
            if not element.is_displayed():
                return {'is_clickable': False, 'reason': 'Not visible'}
            
            if not element.is_enabled():
                return {'is_clickable': False, 'reason': 'Not enabled'}
            
            return {
                'is_clickable': True,
                'reason': 'Element appears clickable',
            }
            
        except Exception as e:
            return {'is_clickable': False, 'reason': f'Error: {str(e)}'}

    def _analyze_url(self, url):
        """Анализ URL"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0] if value else ''
            
            return {
                'domain': parsed.netloc,
                'path': parsed.path,
                'has_utm': len(utm_params) > 0,
                'utm_params': utm_params,
                'query_params_count': len(query_params)
            }
        except:
            return {}

    def _click_element(self, element):
        """Безопасный клик по элементу с обработкой ошибок"""
        try:
            original_url = self.driver.current_url
            original_windows = set(self.driver.window_handles)
            original_window = self.driver.current_window_handle
            
            click_methods = [
                self._try_action_click,
                self._try_action_click_with_offset,
                self._try_simple_click,
                self._try_javascript_click
            ]
            
            result = {
                'success': False,
                'method': None,
                'error': None,
                'original_url': original_url,
                'original_windows': list(original_windows),
                'original_window': original_window
            }

            self.driver.execute_script("arguments[0].scrollIntoView({ block: 'center', inline: 'center' });", element)

            for method in click_methods:
                method_name = method.__name__
                self.logger.info(f"Пробуем метод клика: {method_name}")
                
                try:
                    method(element)
                    
                    time.sleep(6)
                    
                    result['success'] = True
                    result['method'] = method_name
                    
                    current_windows = set(self.driver.window_handles)
                    self.logger.info(current_windows)
                    new_windows = current_windows - original_windows
                    
                    if new_windows:
                        result['new_window_opened'] = True
                        result['new_windows'] = list(new_windows)
                        
                        new_window = next(iter(new_windows))
                        self.driver.switch_to.window(new_window)
                    else:
                        result['new_window_opened'] = False
                        continue
                    
                    break
                    
                except Exception as e:
                    result['error'] = str(e)
                    continue
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'none'
            }

    def _try_simple_click(self, element):
        """Простой клик"""
        element.click()
    
    def _try_javascript_click(self, element):
        """Клик через JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)

    def _try_action_click(self, element):
        """Клик через ActionChains"""
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click().perform()

    def _try_action_click_with_offset(self, element, x = 20, y = -10):
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(element, x, y).click().perform()
        self.logger.info("Клик через ActionChains со смещением")

    def _analyze_redirect(self, original_url, original_windows):
        """Анализ редиректа после клика"""
        try:
            current_url = self.driver.current_url
            current_windows = set(self.driver.window_handles)
            
            analysis = {
                'url_changed': current_url != original_url,
                'new_window_opened': len(current_windows) > len(original_windows),
                'current_url': current_url,
                'original_url': original_url,
                'window_count_change': len(current_windows) - len(original_windows)
            }
            
            if analysis['url_changed']:
                analysis['url_analysis'] = self._analyze_url(current_url)
                
                if current_url.startswith('http'):
                    analysis['is_redirect'] = True
                    
                    parsed_current = urlparse(current_url)
                    query_params = parse_qs(parsed_current.query)
                    
                    redirect_keys = ['redirect', 'return', 'next', 'goto', 'url']
                    has_redirect_param = any(key in query_params for key in redirect_keys)
                    analysis['has_redirect_param'] = has_redirect_param
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}

    def restore_original_state(self, original_window):
        """Восстановление исходного состояния браузера"""
        try:
            current_windows = set(self.driver.window_handles)
            
            for window in current_windows:
                if window != original_window:
                    try:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                    except:
                        pass
            
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.logger.warning(f"Error restoring original state: {str(e)}")
