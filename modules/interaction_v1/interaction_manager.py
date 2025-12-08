import logging
import time
from urllib.parse import urlparse, parse_qs
from config.settings import Settings
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class 

    def click_elements(self, elements):
        logger.info("Начинаем клики по рекламным элементам")
        main_window = self.driver.current_window_handle
        ads_click = []
        try:
            overlaying_element = self.driver.find_element(By.CSS_SELECTOR, "div.widgets__b-slide")
            self.driver.execute_script("arguments[0].style.visibility='hidden'", overlaying_element)
        except NoSuchElementException:
            pass

        for i, element in enumerate(elements, start=1):
            try:
                time.sleep(3)
                ActionChains(self.driver).move_to_element_with_offset(element, -20, -10).click().perform()
                logger.info(f"Клик по {i} элементу")
                WebDriverWait(self.driver, 15).until(EC.number_of_windows_to_be(2))
                
                new_window = [window for window in self.driver.window_handles if window != main_window][0]

                self.driver.switch_to.window(new_window)

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
                logger.error(f"Страница {i} не рагрузилась: {e}")
                continue
            except Exception as e:
                logger.error(f"Не удолось кликнуть по {i} элементу: {e}")
                continue

            ads_click.extend(ad_data)

        return ads_click
    
    def extract_utm_params(self, url, i):
        """Извлекает UTM-метки из URL"""
        try:
            logger.info(f"Извлекает UTM-метки из URL элемента {i}")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0]
        except Exception as e:
            logger.error(f"Ошибка при извлечении UTM-метки: {e}")