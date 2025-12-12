from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
from typing import Optional, Tuple, Callable, Generator, Any, Union
import logging
import time
import random

class RedirectManager:
    """Контекстный менеджер для безопасного управления переходами между окнами/вкладками в Selenium."""

    def __init__(self, driver: WebDriver, element, timeout = 30):
        if not element:
            raise ValueError("Должен быть указан element")
        
        self.driver = driver
        self.element = element
        self.timeout = timeout

        self.original_window = None
        self.original_handles = None
        self.new_window_handle = None

        self.wait = WebDriverWait(self.driver, self.timeout)
        self.logger = logging.getLogger(__name__)
        
    def __enter__(self) -> WebDriver:
        """Выполняем действие и переключаемся на новое окно"""
        self.original_window = self.driver.current_window_handle
        self.original_handles = self.driver.window_handles

        self.logger.info(f"Original window: {self.original_window}")
        self.logger.info(f"Original handles: {self.original_handles}")

        try:
            self._perform_action()

            if not self._wait_for_new_window():
                pass
            
            self._wait_load_page()
            self.new_window_handle = self._get_new_window_handle()

            self.driver.switch_to.window(self.new_window_handle)
            self.logger.info(f"Switched to new window: {self.new_window_handle}")
            return self.driver
        
        except Exception as e:
            self.logger.error(f"Failed to open new window: {e}")
            if self.original_window and self.driver.current_window_handle != self.original_window:
                self.driver.switch_to.window(self.original_window)
            raise


    def _get_new_window_handle(self) -> Optional[str]:
        """Получаем handle нового окна"""
        current_handles = set(self.driver.window_handles)
        new_handles = current_handles - self.original_handles
        
        if new_handles:
            return next(iter(new_handles))
        return None
    
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

    def _click(self, element: WebElement, action_chain: ActionChains) -> None:
        """Безопасный клик с обработкой различных случаев"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        action_chain.pause(random.uniform(1, 2))
        action_chain.move_to_element_with_offset(element, -20, -10).click().perform()

    def _wait_load_page(self):
        """Ожидания рагрузки рекламной страницы"""
        try:
            self.action_chain.pause(random.uniform(2.3, 3.7))

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            self.action_chain.pause(random.uniform(2.3, 3.7))

        except Exception as e:
            self.logger.error(f"Ошибка ожидания рагрузки рекламной страницы: {e}")

    def _wait_for_page_load(self, timeout: Optional[int] = None):
        """Ожидание полной загрузки страницы"""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(random.uniform(0.5, 1.5))  # Дополнительная пауза
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


















