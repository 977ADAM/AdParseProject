import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import StaleElementReferenceException
from config.ad_patterns import AdPatterns
from modules.detection.network_identifier import NetworkIdentifier
from modules.detection.size_analyzer import SizeAnalyzer
from modules.detection.pattern_matcher import PatternMatcher

class AdDetector:
    """Основной класс для обнаружения рекламных элементов"""
    def __init__(self, driver: WebDriver, config):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.network_identifier = NetworkIdentifier()
        self.size_analyzer = SizeAnalyzer()
        self.pattern_matcher = PatternMatcher()
        
    def detect_ads(self):
        """Основной метод обнаружения рекламы на странице"""
        self.logger.info("Запуск процесса обнаружения рекламы")
        all_ads = []
        
        detection_methods = [
            # self._detect_by_iframe,
            # self._detect_by_scripts,
            ("поиск по элементам" , self._detect_by_elements),
            # self._detect_by_attributes,
            # self._detect_by_size
        ]
        
        for method_name, method in detection_methods:
            try:
                ads = method()
                all_ads.extend(ads)
                self.logger.info(f"Метод {method_name} найденны {len(ads)} реклам")
            except Exception as e:
                self.logger.error(f"Ошибка в {method_name}: {e}")

        unique_ads = self._remove_duplicates(all_ads)
        self.logger.info(f"Всего обнаружено уникальных объявлений: {len(unique_ads)}")
        
        return unique_ads
    
    def _detect_by_iframe(self):
        """Обнаружение рекламы в iframe"""
        ads = []
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.logger.info(f"Found {len(iframes)} iframes for analysis")
            
            for iframe in iframes:
                try:
                    ad_data = self._analyze_iframe(iframe)
                    if ad_data:
                        ads.append(ad_data)
                except StaleElementReferenceException:
                    self.logger.debug("Stale iframe element, skipping")
                    continue
                except Exception as e:
                    self.logger.debug(f"Error analyzing iframe: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in iframe detection: {str(e)}")
            
        return ads
    
    def _analyze_iframe(self, iframe):
        """Анализ iframe на признаки рекламы"""
        try:
            src = iframe.get_attribute("src")
            if not src:
                return None
            
            # Проверка домена на принадлежность к рекламным сетям
            network_info = self.network_identifier.identify_by_domain(src)
            if not network_info:
                return None
            
            # Получение информации об элементе
            element_info = self._get_element_info(iframe)
            if not element_info:
                return None
            
            ad_data = {
                'element': iframe,
                'type': 'iframe',
                'network': network_info['network'],
                'confidence': network_info['confidence'],
                'src': src,
                'size': element_info['size'],
                'location': element_info['location'],
                'is_displayed': element_info['is_displayed'],
                'attributes': element_info['attributes'],
                'detection_method': 'iframe_analysis'
            }
            
            return ad_data
            
        except Exception as e:
            self.logger.debug(f"Error in iframe analysis: {str(e)}")
            return None
    
    def _detect_by_scripts(self):
        """Обнаружение рекламных скриптов"""
        ads = []
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            self.logger.info(f"Found {len(scripts)} scripts for analysis")
            
            for script in scripts:
                try:
                    ad_data = self._analyze_script(script)
                    if ad_data:
                        ads.append(ad_data)
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error analyzing script: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in script detection: {str(e)}")
            
        return ads
    
    def _analyze_script(self, script):
        """Анализ script элемента на признаки рекламы"""
        try:
            src = script.get_attribute("src")
            inner_html = script.get_attribute("innerHTML") or ""
            
            # Проверка src атрибута
            network_info = None
            if src:
                network_info = self.network_identifier.identify_by_domain(src)
            
            # Проверка содержимого скрипта
            if not network_info and inner_html:
                network_info = self.network_identifier.identify_by_content(inner_html)
            
            if not network_info:
                return None
            
            element_info = self._get_element_info(script)
            
            ad_data = {
                'element': script,
                'type': 'script',
                'network': network_info['network'],
                'confidence': network_info['confidence'],
                'src': src,
                'content_sample': inner_html[:200] if inner_html else '',
                'size': element_info['size'],
                'location': element_info['location'],
                'is_displayed': element_info['is_displayed'],
                'detection_method': 'script_analysis'
            }
            
            return ad_data
            
        except Exception as e:
            self.logger.debug(f"Error in script analysis: {str(e)}")
            return None
    
    def _detect_by_elements(self):
        """Обнаружение рекламных элементов по классам и ID"""
        ads = []
        try:
            # Поиск по классам
            for pattern in AdPatterns.AD_CLASS_PATTERNS:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, f"[class*='{pattern}']")
                    for element in elements:
                        ad_data = self._analyze_generic_element(element, 'class_pattern')
                        if ad_data:
                            ads.append(ad_data)
                except Exception as e:
                    self.logger.debug(f"Error searching class pattern {pattern}: {str(e)}")
            
            # Поиск по ID
            for pattern in AdPatterns.AD_ID_PATTERNS:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, f"[id*='{pattern}']")
                    for element in elements:
                        ad_data = self._analyze_generic_element(element, 'id_pattern')
                        if ad_data:
                            ads.append(ad_data)
                except Exception as e:
                    self.logger.debug(f"Error searching ID pattern {pattern}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in element detection: {str(e)}")
            
        return ads
    
    def _detect_by_attributes(self):
        """Обнаружение по data атрибутам"""
        ads = []
        try:
            for attr in AdPatterns.AD_DATA_ATTRIBUTES:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, f"[{attr}]")
                    for element in elements:
                        ad_data = self._analyze_generic_element(element, 'data_attribute')
                        if ad_data:
                            ads.append(ad_data)
                except Exception as e:
                    self.logger.debug(f"Error searching data attribute {attr}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in attribute detection: {str(e)}")
            
        return ads
    
    def _detect_by_size(self):
        """Обнаружение по стандартным размерам рекламы"""
        ads = []
        try:
            # Ищем все видимые div элементы
            divs = self.driver.find_elements(By.TAG_NAME, "div")
            self.logger.info(f"Found {len(divs)} divs for size analysis")
            
            for div in divs:
                try:
                    if not div.is_displayed():
                        continue
                        
                    ad_data = self._analyze_by_size(div)
                    if ad_data:
                        ads.append(ad_data)
                        
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error analyzing div size: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in size detection: {str(e)}")
            
        return ads
    
    def _analyze_by_size(self, element):
        """Анализ элемента по размеру"""
        try:
            element_info = self._get_element_info(element)
            size = element_info['size']
            
            # Проверка на стандартные размеры рекламы
            size_match = self.size_analyzer.is_standard_ad_size(size['width'], size['height'])
            if not size_match:
                return None
            
            # Дополнительные проверки для увеличения confidence
            attributes = element_info['attributes']
            class_attr = attributes.get('class', '').lower()
            id_attr = attributes.get('id', '').lower()
            
            # Проверка на рекламные ключевые слова
            has_ad_keywords = any(keyword in class_attr or keyword in id_attr 
                                for keyword in AdPatterns.AD_KEYWORDS)
            
            confidence = 0.7 if has_ad_keywords else 0.5
            
            ad_data = {
                'element': element,
                'type': 'banner',
                'network': 'unknown',
                'confidence': confidence,
                'size': element_info['size'],
                'location': element_info['location'],
                'is_displayed': element_info['is_displayed'],
                'attributes': attributes,
                'detection_method': 'size_analysis',
                'standard_size': size_match
            }
            
            return ad_data
            
        except Exception as e:
            self.logger.debug(f"Error in size analysis: {str(e)}")
            return None
    
    def _analyze_generic_element(self, element, detection_method):
        """Анализ общего элемента на признаки рекламы"""
        try:
            element_info = self._get_element_info(element)
            if not element_info or not element_info['is_displayed']:
                return None
            
            attributes = element_info['attributes']
            class_attr = attributes.get('class', '').lower()
            id_attr = attributes.get('id', '').lower()
            
            # Проверка на рекламные ключевые слова
            ad_score = self.pattern_matcher.calculate_ad_score(class_attr, id_attr, attributes)
            if ad_score < 0.3:
                return None
            
            network_info = self.network_identifier.identify_by_attributes(attributes)
            
            ad_data = {
                'id': element.id.split('.').pop(),
                'element': element,
                'type': 'banner',
                'network': network_info['network'] if network_info else 'unknown',
                'confidence': max(ad_score, network_info['confidence'] if network_info else 0),
                'size': element_info['size'],
                'location': element_info['location'],
                'is_displayed': element_info['is_displayed'],
                'attributes': attributes,
                'detection_method': detection_method,
                'ad_score': ad_score,
                'element_info': element_info
            }
            
            return ad_data
            
        except Exception as e:
            self.logger.debug(f"Error in generic element analysis: {str(e)}")
            return None
    
    def _get_element_info(self, element):
        """Получение базовой информации об элементе"""
        try:
            return {
                'size': element.size,
                'location': element.location,
                'is_displayed': element.is_displayed(),
                'attributes': {
                    'class': element.get_attribute('class') or '',
                    'id': element.get_attribute('id') or '',
                    'src': element.get_attribute('src') or '',
                    'href': element.get_attribute('href') or '',
                    'style': element.get_attribute('style') or '',
                    'width': element.get_attribute('width') or '',
                    'height': element.get_attribute('height') or ''
                }
            }
        except StaleElementReferenceException:
            raise
        except Exception as e:
            self.logger.debug(f"Error getting element info: {str(e)}")
            return None
    
    def _remove_duplicates(self, ads):
        """Удаление дублирующихся рекламных элементов"""
        unique_ads = []
        seen_locations = set()
        
        for ad in ads:
            try:
                location_key = f"{ad['location']['x']}_{ad['location']['y']}_{ad['size']['width']}_{ad['size']['height']}"
                
                if location_key not in seen_locations:
                    seen_locations.add(location_key)
                    unique_ads.append(ad)
                    
            except Exception as e:
                self.logger.debug(f"Error processing ad for deduplication: {str(e)}")
                continue
                
        return unique_ads