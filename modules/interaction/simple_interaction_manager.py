import logging
import time
from urllib.parse import urlparse, parse_qs
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleInteractionManager:
    """Простой и надежный менеджер взаимодействия с рекламой"""
    
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 10)
    
    def analyze_ad_element(self, element, ad_data=None):
        """
        Анализ рекламного элемента
        
        Args:
            element: WebElement рекламного блока
            ad_data: Дополнительные данные о рекламе
            
        Returns:
            dict: Результаты анализа
        """
        try:
            results = {
                'element_info': self._get_element_info(element),
                'click_analysis': self._analyze_clickability(element),
                'url_analysis': {},
                'interaction_result': None,
                'error': None
            }
            
            # Получаем URL элемента
            url = self._get_element_url(element)
            if url:
                results['url_analysis'] = self._analyze_url(url)
            
            # Проверяем возможность клика
            if results['click_analysis']['is_clickable']:
                # Пробуем кликнуть
                click_result = self._safe_click_element(element)
                results['interaction_result'] = click_result
                
                # Если клик успешен, анализируем результат
                if click_result.get('success'):
                    results['redirect_analysis'] = self._analyze_redirect(
                        click_result.get('original_url'),
                        click_result.get('original_windows')
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing ad element: {str(e)}")
            return {
                'element_info': {},
                'click_analysis': {'is_clickable': False},
                'error': str(e)
            }
    
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
        """
        Простой анализ кликабельности элемента
        
        Returns:
            dict: Результаты анализа
        """
        try:
            # Проверяем базовые условия
            if not element.is_displayed():
                return {'is_clickable': False, 'reason': 'Not visible'}
            
            if not element.is_enabled():
                return {'is_clickable': False, 'reason': 'Not enabled'}
            
            # Проверяем размер элемента
            size = element.size
            if size['width'] < 10 or size['height'] < 10:
                return {'is_clickable': False, 'reason': 'Too small'}
            
            # Проверяем, есть ли у элемента события клика
            has_onclick = bool(element.get_attribute('onclick'))
            has_href = bool(element.get_attribute('href'))
            has_role_button = element.get_attribute('role') == 'button'
            
            if not any([has_onclick, has_href, has_role_button]):
                # Проверяем родительские элементы на наличие событий
                parent_clickable = self._check_parent_clickable(element)
                if not parent_clickable:
                    return {'is_clickable': False, 'reason': 'No click handler'}
            
            return {
                'is_clickable': True,
                'reason': 'Element appears clickable',
                'click_handlers': {
                    'onclick': has_onclick,
                    'href': has_href,
                    'role_button': has_role_button
                }
            }
            
        except Exception as e:
            return {'is_clickable': False, 'reason': f'Error: {str(e)}'}
    
    def _check_parent_clickable(self, element, max_depth=3):
        """Проверка родительских элементов на кликабельность"""
        try:
            for i in range(max_depth):
                element = element.find_element(By.XPATH, "..")
                if element.get_attribute('onclick') or element.get_attribute('href'):
                    return True
        except:
            pass
        return False
    
    def _get_element_url(self, element):
        """Получение URL из элемента"""
        # Пробуем получить URL из различных атрибутов
        url = element.get_attribute('href')
        if not url:
            url = element.get_attribute('src')
        if not url:
            url = element.get_attribute('data-href')
        if not url:
            # Ищем ссылку внутри элемента
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                url = link.get_attribute('href')
            except:
                pass
        
        return url
    
    def _analyze_url(self, url):
        """Анализ URL"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Ищем UTM параметры
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0] if value else ''
            
            return {
                'domain': parsed.netloc,
                'path': parsed.path,
                'has_utm': len(utm_params) > 0,
                'utm_params': utm_params,
                'query_params_count': len(query_params),
                'is_external': self._is_external_url(url)
            }
        except:
            return {}
    
    def _is_external_url(self, url):
        """Проверка, является ли URL внешним"""
        try:
            current_domain = urlparse(self.driver.current_url).netloc
            url_domain = urlparse(url).netloc
            return current_domain != url_domain
        except:
            return True
    
    def _safe_click_element(self, element):
        """
        Безопасный клик по элементу с обработкой ошибок
        
        Returns:
            dict: Результаты клика
        """
        try:
            # Сохраняем исходное состояние
            original_url = self.driver.current_url
            original_windows = set(self.driver.window_handles)
            original_window = self.driver.current_window_handle
            
            # Пробуем разные методы клика
            click_methods = [
                self._try_simple_click,
                self._try_javascript_click,
                self._try_action_click
            ]
            
            result = {
                'success': False,
                'method': None,
                'error': None,
                'original_url': original_url,
                'original_windows': list(original_windows),
                'original_window': original_window
            }
            
            for method in click_methods:
                method_name = method.__name__
                self.logger.debug(f"Trying click method: {method_name}")
                
                try:
                    method(element)
                    
                    # Даем время для реакции
                    time.sleep(2)
                    
                    result['success'] = True
                    result['method'] = method_name
                    
                    # Проверяем, открылось ли новое окно
                    current_windows = set(self.driver.window_handles)
                    new_windows = current_windows - original_windows
                    
                    if new_windows:
                        result['new_window_opened'] = True
                        result['new_windows'] = list(new_windows)
                        
                        # Переключаемся на новое окно
                        new_window = next(iter(new_windows))
                        self.driver.switch_to.window(new_window)
                        time.sleep(1)
                    else:
                        result['new_window_opened'] = False
                    
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
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.click()
        actions.perform()
    
    def _analyze_redirect(self, original_url, original_windows):
        """
        Анализ редиректа после клика
        
        Args:
            original_url: URL до клика
            original_windows: Окна до клика
            
        Returns:
            dict: Анализ редиректа
        """
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
            
            # Если URL изменился, анализируем изменения
            if analysis['url_changed']:
                analysis['url_analysis'] = self._analyze_url(current_url)
                
                # Проверяем, был ли это редирект
                if current_url.startswith('http'):
                    analysis['is_redirect'] = True
                    
                    # Ищем редиректные параметры
                    parsed_current = urlparse(current_url)
                    query_params = parse_qs(parsed_current.query)
                    
                    redirect_keys = ['redirect', 'return', 'next', 'goto', 'url']
                    has_redirect_param = any(key in query_params for key in redirect_keys)
                    analysis['has_redirect_param'] = has_redirect_param
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def restore_original_state(self, original_window):
        """
        Восстановление исходного состояния браузера
        
        Args:
            original_window: Исходное окно для возврата
        """
        try:
            current_windows = set(self.driver.window_handles)
            
            # Закрываем все новые окна
            for window in current_windows:
                if window != original_window:
                    try:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                    except:
                        pass
            
            # Возвращаемся в исходное окно
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.logger.warning(f"Error restoring original state: {str(e)}")
    
    def test_multiple_ads(self, ads_data, max_ads=3):
        """
        Тестирование нескольких рекламных блоков
        
        Args:
            ads_data: Список данных о рекламных блоках
            max_ads: Максимальное количество для тестирования
            
        Returns:
            list: Результаты тестирования
        """
        results = []
        
        for i, ad in enumerate(ads_data[:max_ads]):
            try:
                element = ad.get('element')
                if not element:
                    continue
                
                self.logger.info(f"Testing ad {i+1}/{min(len(ads_data), max_ads)}")
                
                # Анализируем элемент
                analysis = self.analyze_ad_element(element, ad)
                
                # Сохраняем результат
                result = {
                    'ad_index': i,
                    'ad_data': {
                        'type': ad.get('type'),
                        'network': ad.get('network'),
                        'confidence': ad.get('confidence')
                    },
                    'analysis': analysis
                }
                
                results.append(result)
                
                # Восстанавливаем состояние
                if analysis.get('interaction_result', {}).get('success'):
                    original_window = analysis['interaction_result'].get('original_window')
                    if original_window:
                        self.restore_original_state(original_window)
                
                # Пауза между тестами
                if i < len(ads_data[:max_ads]) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error testing ad {i+1}: {str(e)}")
                results.append({
                    'ad_index': i,
                    'error': str(e)
                })
        
        return results