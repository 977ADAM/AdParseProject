from contextlib import contextmanager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from typing import Optional, Tuple, Callable, Generator, Any, Union
import logging
import time

class RedirectManager:
    """
    Продвинутый контекстный менеджер для работы с новыми окнами.
    Обрабатывает клик по элементу и автоматический переход.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        element_locator: Optional[Tuple[str, str]] = None,
        element: Optional[WebElement] = None,
        action: Optional[Callable] = None,
        timeout: int = 15,
        close_on_exit: bool = True,
        validate_new_window: bool = True
    ):
        """
        Args:
            driver: WebDriver instance
            element_locator: Локатор элемента для клика (By.XPATH, "//button")
            element: Готовый WebElement для клика
            action: Кастомная функция действия вместо клика
            timeout: Таймаут ожидания
            close_on_exit: Закрывать ли новое окно при выходе
            validate_new_window: Проверять ли загрузку новой страницы
        """
        if not any([element_locator, element, action]):
            raise ValueError("Должен быть указан element_locator, element или action")
        
        self.driver = driver
        self.element_locator = element_locator
        self.element = element
        self.action = action
        self.timeout = timeout
        self.close_on_exit = close_on_exit
        self.validate_new_window = validate_new_window
        
        self.original_window: Optional[str] = None
        self.original_handles: set = set()
        self.new_window_handle: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
    def __enter__(self) -> WebDriver:
        """Выполняем действие и переключаемся на новое окно"""
        
        # 1. Сохраняем текущее состояние
        self.original_window = self.driver.current_window_handle
        self.original_handles = set(self.driver.window_handles)
        self.logger.debug(f"Original window: {self.original_window}")
        self.logger.debug(f"Original handles: {self.original_handles}")
        
        try:
            # 2. Выполняем действие, открывающее новое окно
            self._perform_action()
            
            # 3. Ждем появления нового окна
            self.new_window_handle = self._wait_for_new_window()
            
            # 4. Переключаемся на новое окно
            self.driver.switch_to.window(self.new_window_handle)
            self.logger.info(f"Switched to new window: {self.new_window_handle}")
            
            # 5. Валидируем новое окно
            if self.validate_new_window:
                self._validate_new_window()
            
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to open new window: {e}")
            # При ошибке возвращаемся в исходное окно
            if self.original_window and self.driver.current_window_handle != self.original_window:
                self.driver.switch_to.window(self.original_window)
            raise
    
    def _perform_action(self) -> None:
        """Выполняем действие для открытия нового окна"""
        
        if self.action:
            # Пользовательская функция
            self.action()
            
        elif self.element:
            # Клик по готовому элементу
            self._safe_click(self.element)
            
        elif self.element_locator:
            # Находим элемент и кликаем
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(self.element_locator)
            )
            self._safe_click(element)
            
        else:
            raise RuntimeError("No action specified")
    
    def _safe_click(self, element: WebElement) -> None:
        """Безопасный клик с обработкой различных случаев"""
        try:
            element.click()
        except Exception as e:
            self.logger.warning(f"Standard click failed: {e}, trying JavaScript")
            self.driver.execute_script("arguments[0].click();", element)
    
    def _wait_for_new_window(self) -> str:
        """Ожидаем появления нового окна"""
        wait = WebDriverWait(self.driver, self.timeout)
        
        def new_window_available(driver: WebDriver) -> Union[str, bool]:
            current_handles = set(driver.window_handles)
            new_handles = current_handles - self.original_handles
            
            if new_handles:
                # Возвращаем handle нового окна
                new_handle = next(iter(new_handles))
                # Проверяем, что окно действительно открылось
                driver.switch_to.window(new_handle)
                
                # Быстрая проверка, что это не пустое окно
                try:
                    current_url = driver.current_url
                    if current_url and current_url not in ['about:blank', 'data:']:
                        return new_handle
                except:
                    pass
                
                # Даже если URL пустой, ждем немного
                time.sleep(0.5)
                return new_handle
            
            return False
        
        try:
            new_handle = wait.until(new_window_available)
            return new_handle
        except TimeoutException:
            # Детальная диагностика
            current_handles = set(self.driver.window_handles)
            self.logger.error(
                f"New window not opened. "
                f"Original handles: {len(self.original_handles)}, "
                f"Current handles: {len(current_handles)}, "
                f"Difference: {current_handles - self.original_handles}"
            )
            raise TimeoutException(
                f"Новое окно не открылось в течение {self.timeout} секунд. "
                f"Возможно, элемент открывает URL в этой же вкладке."
            )
    
    def _validate_new_window(self) -> None:
        """Валидация загрузки новой страницы"""
        wait = WebDriverWait(self.driver, self.timeout)
        
        # 1. Ждем загрузки DOM
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 2. Ждем, что URL изменился (не остался about:blank)
        def url_changed(driver):
            current_url = driver.current_url
            return current_url and current_url not in ['about:blank', 'data:']
        
        wait.until(url_changed)
        
        # 3. Дополнительно: ждем появления body или другого элемента
        try:
            wait.until(
                EC.presence_of_element_located(("tag name", "body"))
            )
        except TimeoutException:
            self.logger.warning("Body element not found in new window")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Возвращаемся в исходное окно (и закрываем новое при необходимости)"""
        
        try:
            # 1. Закрываем новое окно, если нужно
            if self.close_on_exit and self.new_window_handle:
                if self.new_window_handle in self.driver.window_handles:
                    self.driver.switch_to.window(self.new_window_handle)
                    self.driver.close()
                    self.logger.debug("Closed new window")
            
            # 2. Возвращаемся в исходное окно
            if self.original_window and self.original_window in self.driver.window_handles:
                self.driver.switch_to.window(self.original_window)
                self.logger.debug(f"Returned to original window: {self.original_window}")
                
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
            
        # 3. Дополнительная очистка при ошибке
        if exc_type is not None:
            self.logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")
            # При ошибке стараемся хотя бы вернуться к исходному окну
            if self.original_window:
                try:
                    self.driver.switch_to.window(self.original_window)
                except:
                    pass


















