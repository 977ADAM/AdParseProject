import pytest
import allure
from allure_commons.types import Severity
from unittest.mock import Mock, MagicMock, patch
from selenium.webdriver.common.by import By
from modules.detection.ad_detector import AdDetector
from config.ad_patterns import AdPatterns

@allure.epic("Detection Module")
@allure.feature("Ad Detector")
class TestAdDetector:
    
    @allure.title("Test ad detection by CSS classes")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.unit
    def test_detect_ads_by_classes(self, mock_driver, mock_config):
        """Тест обнаружения рекламы по CSS"""

        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "yandex_rtb_78654387654"
        mock_element.is_displayed.return_value = True
        mock_element.size = {'width': 300, 'height': 250}
        mock_element.location = {'x': 100, 'y': 200}
        
        mock_driver.find_elements.return_value = [mock_element]
        
        ad_detector = AdDetector(mock_driver, mock_config)
        
        ads = ad_detector._detect_by_elements()
        
        assert len(ads) > 0


    @allure.title("Test comprehensive ad detection")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.unit
    def test_comprehensive_ad_detection(self, mock_driver, mock_config):
        """Тест комплексного обнаружения рекламы"""

        ad_detector = AdDetector(mock_driver, mock_config)

        ads = ad_detector.detect_ads()
        
        assert len(ads) == 1
















    @allure.title("Test duplicate removal")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.unit
    def test_remove_duplicates(self, mock_driver, mock_settings):
        """Тест удаления дублирующихся рекламных блоков"""
        # Arrange
        ad_detector = AdDetector(mock_driver, mock_settings)
        
        duplicate_ads = [
            {'location': {'x': 100, 'y': 200}, 'size': {'width': 300, 'height': 250}},
            {'location': {'x': 100, 'y': 200}, 'size': {'width': 300, 'height': 250}},  # Дубликат
            {'location': {'x': 400, 'y': 500}, 'size': {'width': 728, 'height': 90}}   # Уникальный
        ]
        
        # Act
        unique_ads = ad_detector._remove_duplicates(duplicate_ads)
        
        # Assert
        assert len(unique_ads) == 2
    
    @allure.title("Test element info extraction")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.unit
    def test_get_element_info(self, mock_web_element, mock_driver, mock_settings):
        """Тест извлечения информации об элементе"""
        # Arrange
        ad_detector = AdDetector(mock_driver, mock_settings)
        
        # Act
        element_info = ad_detector._get_element_info(mock_web_element)
        
        # Assert
        assert element_info is not None
        assert 'size' in element_info
        assert 'location' in element_info
        assert 'is_displayed' in element_info
        assert 'attributes' in element_info