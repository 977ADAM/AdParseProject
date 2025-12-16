from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (TimeoutException,
                                        StaleElementReferenceException,
                                        ElementNotInteractableException)
from typing import Optional
import logging
import time
import random

class RedirectManager:
    """Контекстный менеджер для безопасного управления переходами между окнами/вкладками в Selenium."""

    def __init__(self, driver: WebDriver, element: WebElement, original_window: str, timeout: int = 30):
        if not element:
            raise ValueError("Должен быть указан element")
        
        self.driver = driver
        self.element = element
        self.timeout = timeout
        self.original_window = original_window

        self.original_handles = None
        self.new_window_handle = None

        self.logger = logging.getLogger(__name__)
        
    def __enter__(self) -> WebDriver:
        """Выполняем действие и переключаемся на новое окно"""
        try:
            self._validate_driver_state()
            self._save_original_state()
            self._perform_action()
            if not self._wait_for_new_window():
                raise TimeoutException("Новое окно не появилось")
            self._get_new_window_handle()
            self.driver.switch_to.window(self.new_window_handle)
            self.logger.info(f"Переключилось в новое окно: {self.new_window_handle}")
            self._wait_for_page_load()
            return self.driver
        
        except TimeoutException as e:
            self.logger.error(f"Таймаут при открытии нового окна: {e}")
            raise

        except StaleElementReferenceException:
            self.logger.error("Элемент устарел перед кликом")
            raise

        except ElementNotInteractableException:
            self.logger.error("Элемент не доступен для взаимодействия")
            raise

        except Exception as e:
            self.logger.error(f"Не удалось открыть новое окно: {e}")
            if self.original_window and self.driver.current_window_handle != self.original_window:
                self.driver.switch_to.window(self.original_window)
            raise

    def _validate_driver_state(self):
        """Проверка состояния драйвера перед операциями"""
        if not hasattr(self.driver, 'session_id') or not self.driver.session_id:
            raise ValueError("Сессия драйвера не активна")
        try:
            self.driver.current_window_handle
        except Exception:
            raise ValueError("Драйвер не отвечает")
        
    def _save_original_state(self):
        """Сохранение исходного состояния"""
        self.original_handles = list(self.driver.window_handles)
        self.logger.info(f"Оригинальные : окна{self.original_handles}")

    def _get_new_window_handle(self) -> Optional[str]:
        """Получаем handle нового окна"""
        new_handles = set(self.driver.window_handles) - set(self.original_handles)
        if not new_handles:
            raise TimeoutException("Не удалось определить новое окно")
        self.new_window_handle = new_handles.pop()

    
    def _wait_for_new_window(self) -> bool:
        """Ожидание появления нового окна"""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda d: len(d.window_handles) > len(self.original_handles)
            )
            return True
        except TimeoutException:
            return False

    def _perform_action(self) -> None:
        """Выполняем действие для открытия нового окна"""
        action_chain = ActionChains(self.driver)

        action_chain.pause(random.uniform(1.5, 2))

        if self.element:
            self._click(self.element, action_chain)

        action_chain.pause(random.uniform(1.5, 2))

        action_chain.perform()

    def _click(self, element: WebElement, action_chain: ActionChains) -> None:
        """Безопасный клик с обработкой различных случаев"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: element.is_displayed() and element.is_enabled()
        )

        action_chain.pause(random.uniform(1, 2))

        action_chain.move_to_element_with_offset(element, -20, -10).click().perform()

        self.logger.info(f"Клик по рекламе: {element.id}")

    def _wait_for_page_load(self, timeout: int = None):
        """Ожидание полной загрузки страницы"""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
                )
        except TimeoutException:
            self.logger.warning("Страница загрузилась не полностью")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Возвращаемся в исходное окно (и закрываем новое при необходимости)"""
        try:
            if self.new_window_handle and self.new_window_handle in self.driver.window_handles:
                self.driver.switch_to.window(self.new_window_handle)
                self.driver.close()
                self.logger.info("Закрыто новое окно")
            
            if self.original_window and self.original_window in self.driver.window_handles:
                self.driver.switch_to.window(self.original_window)
                self.logger.info(f"Возвращено в исходное окно: {self.original_window}")
            
        except Exception as e:
            self.logger.warning(f"Ошибка во время очистки: {e}")
