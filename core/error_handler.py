import logging
from selenium.common.exceptions import (
    WebDriverException, 
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException
)

class ErrorHandler:
    """Централизованная обработка ошибок Selenium"""
    logger = logging.getLogger(__name__)
    
    @staticmethod
    def handle_driver_error(error):
        """Обработка ошибок WebDriver"""
        if isinstance(error, TimeoutException):
            ErrorHandler.logger.warning("Page load timeout occurred")
            return "TIMEOUT_ERROR"
        elif isinstance(error, WebDriverException):
            ErrorHandler.logger.error(f"WebDriver error: {str(error)}")
            return "DRIVER_ERROR"
        else:
            ErrorHandler.logger.error(f"Unexpected error: {str(error)}")
            return "UNKNOWN_ERROR"
    
    @staticmethod
    def handle_element_error(error, element_description=""):
        """Обработка ошибок при работе с элементами"""
        if isinstance(error, NoSuchElementException):
            ErrorHandler.logger.debug(f"Element not found: {element_description}")
            return "ELEMENT_NOT_FOUND"
        elif isinstance(error, StaleElementReferenceException):
            ErrorHandler.logger.warning(f"Stale element: {element_description}")
            return "STALE_ELEMENT"
        else:
            ErrorHandler.logger.warning(f"Element error: {str(error)}")
            return "ELEMENT_ERROR"