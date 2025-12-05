import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from selenium.webdriver.remote.webelement import WebElement
from modules.detection.ad_detector import AdDetector
from config.ad_patterns import AdPatterns
import logging

class TestAdDetector(unittest.TestCase):
    """Unit тесты для модуля обнаружения рекламы"""
    
    def setUp(self):
        """Подготовка тестового окружения"""
        # Мокаем драйвер и конфиг
        self.mock_driver = Mock()
        self.mock_config = Mock()
        self.mock_config.PAGE_LOAD_TIMEOUT = 30
        
        # Создаем экземпляр детектора с моками
        self.detector = AdDetector(self.mock_driver, self.mock_config)
        
        # Отключаем логирование для чистоты тестов
        logging.getLogger('modules.detection.ad_detector').setLevel(logging.CRITICAL)
    
    def test_initialization(self):
        """Тест инициализации детектора"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.driver, self.mock_driver)
        self.assertEqual(self.detector.config, self.mock_config)
        self.assertIsNotNone(self.detector.network_identifier)
        self.assertIsNotNone(self.detector.size_analyzer)
        self.assertIsNotNone(self.detector.pattern_matcher)
    
    def test_detect_ads_no_elements(self):
        """Тест обнаружения рекламы, когда элементов нет"""
        # Настраиваем моки
        self.mock_driver.find_elements.return_value = []
        
        # Вызываем метод
        result = self.detector.detect_ads()
        
        # Проверяем результат
        self.assertEqual(result, [])
        self.mock_driver.find_elements.assert_called()
    
    @patch.object(AdDetector, '_detect_by_iframe')
    @patch.object(AdDetector, '_detect_by_scripts')
    @patch.object(AdDetector, '_detect_by_elements')
    @patch.object(AdDetector, '_detect_by_attributes')
    @patch.object(AdDetector, '_detect_by_size')
    def test_detect_ads_all_methods_called(self, mock_size, mock_attr, mock_elem, mock_scripts, mock_iframe):
        """Тест что все методы обнаружения вызываются"""
        # Настраиваем моки возвращать пустые списки
        mock_iframe.return_value = []
        mock_scripts.return_value = []
        mock_elem.return_value = []
        mock_attr.return_value = []
        mock_size.return_value = []
        
        # Вызываем метод
        result = self.detector.detect_ads()
        
        # Проверяем что все методы были вызваны
        mock_iframe.assert_called_once()
        mock_scripts.assert_called_once()
        mock_elem.assert_called_once()
        mock_attr.assert_called_once()
        mock_size.assert_called_once()
        
        # Проверяем результат
        self.assertEqual(result, [])
    
    @patch.object(AdDetector, '_remove_duplicates')
    def test_detect_ads_with_duplicates_removal(self, mock_remove_dups):
        """Тест удаления дубликатов в результатах"""
        # Подготавливаем тестовые данные
        fake_ad = {
            'element': Mock(),
            'type': 'iframe',
            'network': 'google_ads',
            'confidence': 0.9
        }
        
        # Настраиваем мок для удаления дубликатов
        mock_remove_dups.return_value = [fake_ad]
        
        # Патчим все методы обнаружения чтобы возвращали одинаковые данные
        with patch.multiple(AdDetector,
            _detect_by_iframe=Mock(return_value=[fake_ad, fake_ad]),
            _detect_by_scripts=Mock(return_value=[]),
            _detect_by_elements=Mock(return_value=[]),
            _detect_by_attributes=Mock(return_value=[]),
            _detect_by_size=Mock(return_value=[])):
            
            # Вызываем метод
            result = self.detector.detect_ads()
            
            # Проверяем что remove_duplicates был вызван
            mock_remove_dups.assert_called_once()
            
            # Проверяем результат
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['type'], 'iframe')
            self.assertEqual(result[0]['network'], 'google_ads')
    
    def test_analyze_iframe_with_ad_network(self):
        """Тест анализа iframe с рекламной сетью"""
        # Создаем mock iframe элемент
        mock_iframe = Mock(spec=WebElement)
        mock_iframe.get_attribute.return_value = 'https://doubleclick.net/ad'
        mock_iframe.size = {'width': 300, 'height': 250}
        mock_iframe.location = {'x': 100, 'y': 200}
        mock_iframe.is_displayed.return_value = True
        
        # Патчим network_identifier
        with patch.object(self.detector.network_identifier, 'identify_by_domain') as mock_identify:
            mock_identify.return_value = {
                'network': 'google_ads',
                'confidence': 0.9,
                'matched_domain': 'doubleclick.net'
            }
            
            # Вызываем метод
            result = self.detector._analyze_iframe(mock_iframe)
            
            # Проверяем результат
            self.assertIsNotNone(result)
            self.assertEqual(result['type'], 'iframe')
            self.assertEqual(result['network'], 'google_ads')
            self.assertEqual(result['confidence'], 0.9)
            self.assertEqual(result['detection_method'], 'iframe_analysis')
            
            # Проверяем что get_attribute был вызван
            mock_iframe.get_attribute.assert_called_with('src')
    
    def test_analyze_iframe_no_src(self):
        """Тест анализа iframe без src атрибута"""
        mock_iframe = Mock(spec=WebElement)
        mock_iframe.get_attribute.return_value = None  # Нет src
        
        result = self.detector._analyze_iframe(mock_iframe)
        self.assertIsNone(result)
    
    def test_analyze_iframe_stale_element(self):
        """Тест обработки устаревшего элемента"""
        mock_iframe = Mock(spec=WebElement)
        mock_iframe.get_attribute.side_effect = Exception('Stale element')
        
        # Проверяем что исключение обрабатывается
        result = self.detector._analyze_iframe(mock_iframe)
        self.assertIsNone(result)
    
    def test_analyze_script_with_ad_content(self):
        """Тест анализа script элемента с рекламным контентом"""
        mock_script = Mock(spec=WebElement)
        mock_script.get_attribute.side_effect = lambda attr: {
            'src': 'https://googletagmanager.com/gtag/js',
            'innerHTML': 'googletag.cmd.push(function() { googletag.display("ad-slot"); });'
        }.get(attr, '')
        
        mock_script.size = {'width': 0, 'height': 0}
        mock_script.location = {'x': 0, 'y': 0}
        mock_script.is_displayed.return_value = False
        
        # Патчим network_identifier
        with patch.object(self.detector.network_identifier, 'identify_by_content') as mock_identify:
            mock_identify.return_value = {
                'network': 'google_ads',
                'confidence': 0.8,
                'matched_pattern': 'googletag'
            }
            
            result = self.detector._analyze_script(mock_script)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['type'], 'script')
            self.assertEqual(result['network'], 'google_ads')
            self.assertIn('content_sample', result)
    
    def test_remove_duplicates_basic(self):
        """Тест базового удаления дубликатов"""
        ads = [
            {
                'element': Mock(),
                'location': {'x': 100, 'y': 200},
                'size': {'width': 300, 'height': 250}
            },
            {
                'element': Mock(),
                'location': {'x': 100, 'y': 200},  # Та же позиция и размер
                'size': {'width': 300, 'height': 250}
            },
            {
                'element': Mock(),
                'location': {'x': 400, 'y': 500},  # Другая позиция
                'size': {'width': 728, 'height': 90}
            }
        ]
        
        result = self.detector._remove_duplicates(ads)
        
        # Должно остаться 2 уникальных элемента
        self.assertEqual(len(result), 2)
    
    def test_remove_duplicates_empty_list(self):
        """Тест удаления дубликатов из пустого списка"""
        result = self.detector._remove_duplicates([])
        self.assertEqual(result, [])
    
    def test_remove_duplicates_invalid_data(self):
        """Тест удаления дубликатов с некорректными данными"""
        ads = [
            {
                'element': Mock(),
                'location': {'x': 100},  # Неполные данные
                'size': {'width': 300}
            },
            None,  # None элемент
            {
                'element': Mock(),
                'location': {'x': 100, 'y': 200},
                'size': {'width': 300, 'height': 250}
            }
        ]
        
        # Проверяем что не падает с ошибкой
        result = self.detector._remove_duplicates(ads)
        self.assertGreaterEqual(len(result), 0)
    
    def test_get_element_info_valid(self):
        """Тест получения информации о корректном элементе"""
        mock_element = Mock(spec=WebElement)
        mock_element.size = {'width': 300, 'height': 250}
        mock_element.location = {'x': 100, 'y': 200}
        mock_element.is_displayed.return_value = True
        
        # Настраиваем get_attribute для разных атрибутов
        def get_attribute_side_effect(attr):
            attrs = {
                'class': 'ad-container banner',
                'id': 'ad-slot-1',
                'src': 'https://example.com/ad.jpg',
                'href': 'https://example.com/click',
                'style': 'display: block;',
                'width': '300',
                'height': '250'
            }
            return attrs.get(attr, '')
        
        mock_element.get_attribute.side_effect = get_attribute_side_effect
        
        result = self.detector._get_element_info(mock_element)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['size'], {'width': 300, 'height': 250})
        self.assertEqual(result['location'], {'x': 100, 'y': 200})
        self.assertTrue(result['is_displayed'])
        self.assertEqual(result['attributes']['class'], 'ad-container banner')
        self.assertEqual(result['attributes']['id'], 'ad-slot-1')
    
    def test_get_element_info_stale(self):
        """Тест получения информации об устаревшем элементе"""
        mock_element = Mock(spec=WebElement)
        mock_element.size = {'width': 300, 'height': 250}
        mock_element.location = {'x': 100, 'y': 200}
        mock_element.is_displayed.side_effect = Exception('Stale element')
        
        # Проверяем что исключение пробрасывается
        with self.assertRaises(Exception):
            self.detector._get_element_info(mock_element)
    
    @patch('modules.detection.ad_detector.SizeAnalyzer')
    def test_analyze_by_size_standard_ad(self, mock_size_analyzer_class):
        """Тест анализа по стандартным размерам рекламы"""
        mock_element = Mock(spec=WebElement)
        
        # Создаем mock size_analyzer
        mock_size_analyzer = Mock()
        mock_size_analyzer.is_standard_ad_size.return_value = '300x250'
        self.detector.size_analyzer = mock_size_analyzer
        
        # Патчим _get_element_info
        with patch.object(self.detector, '_get_element_info') as mock_get_info:
            mock_get_info.return_value = {
                'size': {'width': 300, 'height': 250},
                'location': {'x': 100, 'y': 200},
                'is_displayed': True,
                'attributes': {
                    'class': 'ad-banner',
                    'id': 'ad-1'
                }
            }
            
            result = self.detector._analyze_by_size(mock_element)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['type'], 'banner')
            self.assertEqual(result['standard_size'], '300x250')
            self.assertIn('confidence', result)
    
    def test_detect_ads_with_exception_handling(self):
        """Тест обработки исключений в detect_ads"""
        # Создаем детектор и патчим один из методов чтобы он бросал исключение
        with patch.object(self.detector, '_detect_by_iframe') as mock_iframe:
            mock_iframe.side_effect = Exception("Test exception")
            
            # Другие методы должны работать нормально
            with patch.object(self.detector, '_detect_by_scripts') as mock_scripts:
                mock_scripts.return_value = []
                
                # Метод не должен падать из-за исключения в одном из детекторов
                result = self.detector.detect_ads()
                
                # Проверяем что метод завершился и вернул результат
                self.assertIsNotNone(result)
                self.assertEqual(result, [])
                
                # Проверяем что методы были вызваны
                mock_iframe.assert_called_once()
                mock_scripts.assert_called_once()


class TestAdDetectorIntegration(unittest.TestCase):
    """Интеграционные тесты с реальными паттернами"""
    
    def setUp(self):
        self.mock_driver = Mock()
        self.mock_config = Mock()
        self.detector = AdDetector(self.mock_driver, self.mock_config)
    
    def test_pattern_matching_integration(self):
        """Интеграционный тест совпадения с паттернами"""
        # Создаем элемент с классом содержащим рекламный паттерн
        mock_element = Mock(spec=WebElement)
        
        # Настраиваем элемент с явным рекламным классом
        def get_attribute_side_effect(attr):
            if attr == 'class':
                return 'adsbygoogle ad-container'
            elif attr == 'id':
                return 'div-gpt-ad-123'
            return ''
        
        mock_element.get_attribute.side_effect = get_attribute_side_effect
        mock_element.size = {'width': 300, 'height': 250}
        mock_element.location = {'x': 100, 'y': 200}
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True
        mock_element.tag_name = 'div'
        
        # Патчим методы для контролируемого тестирования
        with patch.object(self.detector, '_get_element_info') as mock_get_info:
            mock_get_info.return_value = {
                'size': {'width': 300, 'height': 250},
                'location': {'x': 100, 'y': 200},
                'is_displayed': True,
                'attributes': {
                    'class': 'adsbygoogle ad-container',
                    'id': 'div-gpt-ad-123',
                    'src': '',
                    'href': '',
                    'style': '',
                    'width': '',
                    'height': ''
                }
            }
            
            # Патчим network_identifier для возврата google_ads
            with patch.object(self.detector.network_identifier, 'identify_by_attributes') as mock_identify:
                mock_identify.return_value = {
                    'network': 'google_ads',
                    'confidence': 0.9
                }
                
                # Патчим pattern_matcher для возврата высокого score
                with patch.object(self.detector.pattern_matcher, 'calculate_ad_score') as mock_score:
                    mock_score.return_value = 0.8
                    
                    # Вызываем метод анализа элемента
                    result = self.detector._analyze_generic_element(mock_element, 'class_pattern')
                    
                    # Проверяем результат
                    self.assertIsNotNone(result)
                    self.assertEqual(result['network'], 'google_ads')
                    self.assertEqual(result['detection_method'], 'class_pattern')
                    self.assertGreaterEqual(result['confidence'], 0.8)


if __name__ == '__main__':
    unittest.main()