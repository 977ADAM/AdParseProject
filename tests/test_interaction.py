import pytest
import allure
from allure_commons.types import Severity
import time
from unittest.mock import MagicMock, patch, call
from selenium.common.exceptions import ElementClickInterceptedException
from modules.interaction.interaction_manager_version1 import InteractionManager

@allure.epic("Interaction Module")
@allure.feature("Click Emulator")
class TestClickEmulator:
    
    @allure.title("Тестовый анализ кликабельности — успешный клик")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.unit
    def test_analyze_clickability_success(self, mock_driver, mock_config, mock_web_element):
        """Тест анализа кликабельности - успешный клик"""

        click_emulator = InteractionManager(mock_driver, mock_config)
        
        result = click_emulator._click_element(mock_web_element)
        
        assert result['success'] == True

    @allure.title("Тестовый анализ кликабельности — элемент не виден")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.unit
    def test_analyze_clickability_not_visible(self, mock_driver, mock_config, mock_web_element):
        """Тест анализа кликабельности - элемент не видим"""

        mock_web_element.is_displayed.return_value = False
        
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        result = click_emulator._click_element(mock_web_element)
        
        assert result['is_clickable'] is False
    
    @allure.title("Test direct click method")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.unit
    def test_try_direct_click(self, mock_driver, mock_config, mock_web_element):
        """Тест метода прямого клика"""
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        result = click_emulator._try_direct_click(mock_web_element)
        
        assert result['success'] is True
        mock_web_element.click.assert_called_once()
    
    @allure.title("Test direct click intercepted")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.unit
    def test_try_direct_click_intercepted(self, mock_driver, mock_config, mock_web_element):
        """Тест перехваченного прямого клика"""
        # Arrange
        mock_web_element.click.side_effect = ElementClickInterceptedException("Intercepted")
        
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        # Act
        result = click_emulator._try_direct_click(mock_web_element)
        
        # Assert
        assert result['success'] is False
        assert 'intercepted' in result['error'].lower()
    
    @allure.title("Test JavaScript click method")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.unit
    def test_try_javascript_click(self, mock_driver, mock_config, mock_web_element):
        """Тест метода клика через JavaScript"""
        # Arrange
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        # Act
        result = click_emulator._try_javascript_click(mock_web_element)
        
        # Assert
        assert result['success'] is True
        mock_driver.execute_script.assert_called_with("arguments[0].click();", mock_web_element)
    
    @allure.title("Test human click emulation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.unit
    @pytest.mark.slow
    def test_emulate_human_click(self, mock_driver, mock_config, mock_web_element):
        """Тест эмуляции человеческого клика"""
        # Arrange
        mock_driver.current_window_handle = "window1"
        mock_driver.window_handles = ["window1"]
        mock_driver.current_url = "https://example.com"
        
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        # Мокаем подготовку и выполнение клика
        with patch.object(click_emulator, '_prepare_for_click'):
            with patch.object(click_emulator, '_execute_human_click', 
                           return_value={'success': True, 'method': 'human_direct_click'}):
                with patch.object(click_emulator, '_analyze_click_result',
                               return_value={'new_window_opened': False, 'url_changed': True}):
                    # Act
                    result = click_emulator.emulate_human_click(mock_web_element, click_delay=0.1)
        
        # Assert
        assert result['success'] is True
        assert 'click_method' in result
        assert 'result_analysis' in result
    
    @allure.title("Test click result analysis")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.unit
    def test_analyze_click_result(self, mock_driver, mock_config):
        """Тест анализа результата клика"""
        # Arrange
        mock_driver.current_window_handle = "window1"
        mock_driver.window_handles = ["window1", "window2"]  # Новое окно открылось
        mock_driver.current_url = "https://redirected.com"
        
        click_emulator = InteractionManager(mock_driver, mock_config)
        
        original_window = "window1"
        original_windows = {"window1"}
        original_url = "https://example.com"
        
        # Act
        result = click_emulator._analyze_click_result(original_window, original_windows, original_url)
        
        # Assert
        assert result['new_window_opened'] is True
        assert result['url_changed'] is True
        assert result['windows_count_change'] == 1