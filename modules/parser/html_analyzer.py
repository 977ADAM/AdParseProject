import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from core.error_handler import ErrorHandler

class HTMLAnalyzer:
    """Класс для анализа HTML структуры страницы"""
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()
    
    def get_all_elements(self, element_type='*'):
        """
        Получение всех элементов указанного типа
        
        Args:
            element_type (str): Тип элемента (tag name)
            
        Returns:
            list: Список элементов
        """
        try:
            return self.driver.find_elements(By.TAG_NAME, element_type)
        except Exception as e:
            self.logger.error(f"Error getting elements {element_type}: {str(e)}")
            return []
    
    def find_elements_by_xpath(self, xpath):
        """
        Поиск элементов по XPath
        
        Args:
            xpath (str): XPath выражение
            
        Returns:
            list: Найденные элементы
        """
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except Exception as e:
            self.logger.error(f"Error finding elements by XPath {xpath}: {str(e)}")
            return []
    
    def get_element_info(self, element):
        """
        Получение информации об элементе
        
        Args:
            element: WebElement
            
        Returns:
            dict: Информация об элементе
        """
        try:
            tag_name = element.tag_name.lower()
            attributes = self._get_element_attributes(element)
            
            info = {
                'tag_name': tag_name,
                'attributes': attributes,
                'text': element.text[:200] if element.text else '',  # Ограничиваем длину текста
                'location': element.location,
                'size': element.size,
                'is_displayed': element.is_displayed(),
                'is_enabled': element.is_enabled(),
                'parent_info': self._get_parent_info(element)
            }
            
            return info
            
        except StaleElementReferenceException:
            self.logger.debug("Stale element reference when getting element info")
            return None
        except Exception as e:
            self.logger.error(f"Error getting element info: {str(e)}")
            return None
    
    def _get_element_attributes(self, element):
        """Получение атрибутов элемента"""
        try:
            attributes = {}
            common_attrs = ['id', 'class', 'src', 'href', 'alt', 'title', 'width', 'height', 
                           'style', 'data-*', 'onclick', 'onload']
            
            for attr in common_attrs:
                if attr == 'data-*':
                    # Получаем все data-атрибуты
                    data_attrs = element.get_attribute('outerHTML')
                    if data_attrs:
                        import re
                        data_matches = re.findall(r'data-([^=]+)="([^"]*)"', data_attrs)
                        for key, value in data_matches:
                            attributes[f'data-{key}'] = value
                else:
                    value = element.get_attribute(attr)
                    if value:
                        attributes[attr] = value
            
            return attributes
            
        except Exception as e:
            self.logger.warning(f"Error getting element attributes: {str(e)}")
            return {}
    
    def _get_parent_info(self, element, levels=3):
        """Получение информации о родительских элементах"""
        try:
            parents = []
            current = element
            
            for i in range(levels):
                try:
                    current = current.find_element(By.XPATH, "..")
                    tag = current.tag_name.lower()
                    class_attr = current.get_attribute('class') or ''
                    id_attr = current.get_attribute('id') or ''
                    
                    parents.append({
                        'level': i + 1,
                        'tag': tag,
                        'class': class_attr,
                        'id': id_attr
                    })
                except NoSuchElementException:
                    break
                    
            return parents
            
        except Exception as e:
            self.logger.debug(f"Error getting parent info: {str(e)}")
            return []
    
    def get_page_structure(self):
        """Анализ общей структуры страницы Returns: dict: Структура страницы"""
        try:
            structure = {
                'head': self._analyze_head(),
                'body': self._analyze_body(),
                'scripts': self._analyze_scripts(),
                'iframes': self._analyze_iframes(),
                'links': self._analyze_links(),
                'images': self._analyze_images()
            }
            return structure
        except Exception as e:
            self.logger.error(f"Error analyzing page structure: {str(e)}")
            return {}
    
    def _analyze_head(self):
        """Анализ head раздела"""
        try:
            head = self.driver.find_element(By.TAG_NAME, "head")
            return {
                'title': head.find_element(By.TAG_NAME, "title").text if head.find_elements(By.TAG_NAME, "title") else '',
                'meta_tags': len(head.find_elements(By.TAG_NAME, "meta")),
                'link_tags': len(head.find_elements(By.TAG_NAME, "link")),
                'script_tags': len(head.find_elements(By.TAG_NAME, "script"))
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing head: {str(e)}")
            return {}
    
    def _analyze_body(self):
        """Анализ body раздела"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            return {
                'total_elements': len(body.find_elements(By.XPATH, ".//*")),
                'div_count': len(body.find_elements(By.TAG_NAME, "div")),
                'span_count': len(body.find_elements(By.TAG_NAME, "span")),
                'a_count': len(body.find_elements(By.TAG_NAME, "a")),
                'img_count': len(body.find_elements(By.TAG_NAME, "img"))
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing body: {str(e)}")
            return {}
    
    def _analyze_scripts(self):
        """Анализ скриптов"""
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            script_info = []
            
            for script in scripts[:10]:
                src = script.get_attribute('src')
                if src:
                    script_info.append({
                        'src': src,
                        'type': script.get_attribute('type') or 'text/javascript'
                    })
            
            return {
                'total_scripts': len(scripts),
                'external_scripts': len([s for s in scripts if s.get_attribute('src')]),
                'sample_scripts': script_info
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing scripts: {str(e)}")
            return {}
    
    def _analyze_iframes(self):
        """Анализ iframe"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            iframe_info = []
            
            for iframe in iframes[:5]:  # Ограничиваем количество
                src = iframe.get_attribute('src')
                iframe_info.append({
                    'src': src,
                    'size': iframe.size,
                    'location': iframe.location
                })
            
            return {
                'total_iframes': len(iframes),
                'sample_iframes': iframe_info
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing iframes: {str(e)}")
            return {}
    
    def _analyze_links(self):
        """Анализ ссылок"""
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            link_info = []
            
            for link in links[:20]:
                href = link.get_attribute('href')
                if href:
                    link_info.append({
                        'href': href,
                        'text': link.text[:100] if link.text else '',
                        'target': link.get_attribute('target') or '_self'
                    })
            
            return {
                'total_links': len(links),
                'sample_links': link_info
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing links: {str(e)}")
            return {}
    
    def _analyze_images(self):
        """Анализ изображений"""
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            image_info = []
            
            for img in images[:10]:
                image_info.append({
                    'src': img.get_attribute('src'),
                    'alt': img.get_attribute('alt') or '',
                    'size': img.size,
                    'location': img.location
                })
            
            return {
                'total_images': len(images),
                'sample_images': image_info
            }
        except Exception as e:
            self.logger.warning(f"Error analyzing images: {str(e)}")
            return {}