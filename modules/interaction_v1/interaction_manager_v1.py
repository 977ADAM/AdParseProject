import logging
import time
import json
import random
from urllib.parse import urlparse, parse_qs
from config.settings import Settings
from .redirect_manager import RedirectManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

class InteractionManagerV1:
    """Главный класс для управления всем процессом взаимодействия с рекламой"""
    def __init__(self, driver: WebDriver, config: Settings):
        self.driver = driver
        self.config = config
        self.action_chain = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 30)
        self.logger = logging.getLogger(__name__)

    def click_elements(self, ads_data):
        self.logger.info("Начинаем клики по рекламным элементам")
        main_window = self.driver.current_window_handle
        results = []

        for i, ad in enumerate(ads_data, start=1):
            try:
                element = ad.get('element')
                if not element:
                    continue

                click_result = self._click(element, i)

                if not click_result['success']:
                    self.logger.warning(f"Не удалось кликнуть по элементу {i} переходим ко следующему элементу")
                    continue
                
                analyze_redirect_result = self._analyze_redirect(main_window)

                ad_data = {
                    "ad_data": ad,
                    "analyze_redirect": analyze_redirect_result,
                    "click_analysis": click_result
                }
                self.logger.info(json.dumps(ad_data, indent=2, ensure_ascii=False))

                results.append(ad_data)

            except TimeoutException as e:
                self.logger.error(f"Страница {i} не рагрузилась: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Не удолось кликнуть по {i} элементу: {e}")
                continue

        return results

    def extract_utm_params(self, url):
        """Извлекает UTM-метки из URL"""
        try:
            self.logger.info(f"Извлекает UTM-метки из URL элемента")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            utm_params = {}

            for key, value in query_params.items():

                if key.startswith('utm_'):

                    utm_params[key] = value[0]
            
            return utm_params

        except Exception as e:
            self.logger.error(f"Ошибка при извлечении UTM-метки: {e}")

    def _wait_load_page(self):
        """Ожидания рагрузки рекламной страницы"""
        try:
            self.action_chain.pause(random.uniform(2.3, 3.7))

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            self.action_chain.pause(random.uniform(2.3, 3.7))

        except TimeoutException:
            self.logger.warning("Страница не загрузиласть полностью")

        except Exception as e:
            self.logger.error(f"Ошибка ожидания рагрузки рекламной страницы: {e}")

    def _click(self, element, i):
        try:
            result = {
                'success': False,
                'is_clickable': False,
                'click_method': None,
                'error': None,
            }

            self.action_chain.pause(random.uniform(1.33, 2.55))

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

            self.action_chain.pause(random.uniform(1.33, 2.55))

            self.action_chain.move_to_element_with_offset(element, -20, -10).click().perform()

            self.action_chain.pause(random.uniform(2.77, 3.55))

            self.logger.info(f"Клик по {i} элементу")

            if element.is_displayed():
                result['is_clickable'] = True

            if len(self.driver.window_handles) == 2:
                self.wait.until(EC.number_of_windows_to_be(2))

                result['success'] = True

                result['click_method'] = 'КЛИК СО СМЕЩЕНИЕМ'

        except Exception as e:
            self.logger.warning(f"Ошибка: {e}")
            result['error'] = e

        return result

    def close(self, main_window):
        try:
            self.driver.close()
            self.driver.switch_to.window(main_window)
        except Exception as e:
            self.logger.warning(f"Ошибка восстановления исходного состояния: {e}")

    def _analyze_redirect(self, main_window):
        try:
            new_window = [window for window in self.driver.window_handles if window != main_window][0]

            self.driver.switch_to.window(new_window)

            self._wait_load_page()

            current_url = self.driver.current_url

            utm_data = self.extract_utm_params(current_url)

            self.close(main_window)
            
            return {
                "utm_data": utm_data,
                "current_url": current_url
            }
        except Exception as e:
            pass

    def perform_complete_ad_interaction(self, data):
        """Выполнение полного цикла взаимодействия с рекламным блоком"""
        self.logger.info("Начинаем клики по рекламным элементам")
        original_window = self.driver.current_window_handle
        self.logger.info(f"Исходное окно: {original_window}")
        results = []

        for ad in data:

            element = ad.get('element')
            if not element:
                continue
            
            redirect_manager = RedirectManager(self.driver, element, original_window)

            with redirect_manager as redirect:
                current_url = redirect.current_url

            self.logger.info(current_url)

            utm_data = self.extract_utm_params(current_url)

            self.logger.info(utm_data)

            ad_data = {
                "ad_data": ad,
                "utm_data": utm_data,
            }

            results.append(ad_data)

        return results