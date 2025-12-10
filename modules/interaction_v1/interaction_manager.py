import logging
import time
import random
from urllib.parse import urlparse, parse_qs
from config.settings import Settings
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

class InteractionManager:
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
        ads_click = []

        for i, ad in enumerate(ads_data, start=1):
            try:
                element = ad.get('element')
                if not element:
                    continue
                
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(3.344)
                self.action_chain.move_to_element_with_offset(element, -20, -10).click().perform()

                self.logger.info(f"Клик по {i} элементу")

                self.action_chain.pause(random.uniform(2.33, 3.55))

                if len(self.driver.window_handles) != 2:
                    self.logger.warning(f"Не удалось кликнуть по элементу {i} переходим ко следующему элементу")
                    continue

                
                self.wait.until(EC.number_of_windows_to_be(2))
                
                new_window = [window for window in self.driver.window_handles if window != main_window][0]

                self.driver.switch_to.window(new_window)
                time.sleep(5)
                self.wait_load_page()

                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

                self.action_chain.pause(random.uniform(1.3, 3.5))

                current_url = self.driver.current_url

                utm_data = self.extract_utm_params(current_url, i)

                ad_data = [{
                    "id": element.id,
                    "current_url": current_url,
                    "title": self.driver.title,
                    "utm_params": utm_data
                }]

                self.driver.close()
                self.driver.switch_to.window(main_window)

            except TimeoutException as e:
                self.logger.error(f"Страница {i} не рагрузилась: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Не удолось кликнуть по {i} элементу: {e}")
                continue

            self.logger.info(utm_data)

            ads_click.extend(ad_data)

        
        return ads_click
    
    def extract_utm_params(self, url, i):
        """Извлекает UTM-метки из URL"""
        try:
            self.logger.info(f"Извлекает UTM-метки из URL элемента {i}")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0]
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении UTM-метки: {e}")
        return utm_params
    
    def wait_load_page(self):
        """Ожидания рагрузки рекламной страницы"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            self.logger.warning("Страница не загрузиласть полностью")
        except Exception as e:
            self.logger.error(f"Ошибка ожидания рагрузки рекламной страницы: {e}")
        