import logging
from config.ad_patterns import AdPatterns

class PatternMatcher:
    """Класс для сопоставления с рекламными паттернами"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_ad_score(self, class_attr, id_attr, attributes):
        """Расчет confidence score для элемента"""
        score = 0.0
        
        # Проверка классов
        class_score = self._check_class_patterns(class_attr)
        score = max(score, class_score)
        
        # Проверка ID
        id_score = self._check_id_patterns(id_attr)
        score = max(score, id_score)
        
        # Проверка data атрибутов
        data_score = self._check_data_attributes(attributes)
        score = max(score, data_score)
        
        # Проверка других атрибутов
        other_score = self._check_other_attributes(attributes)
        score = max(score, other_score)
        
        return score
    
    def _check_class_patterns(self, class_attr):
        """Проверка классов на рекламные паттерны"""
        if not class_attr:
            return 0.0
            
        class_lower = class_attr.lower()
        
        # Точные совпадения
        for pattern in AdPatterns.AD_CLASS_PATTERNS:
            if pattern in class_lower:
                if len(pattern) > 3:
                    return 0.8
                else:
                    return 0.6
        
        return 0.0
    
    def _check_id_patterns(self, id_attr):
        """Проверка ID на рекламные паттерны"""
        if not id_attr:
            return 0.0
            
        id_lower = id_attr.lower()
        
        for pattern in AdPatterns.AD_ID_PATTERNS:
            if pattern in id_lower:
                return 0.7
                
        return 0.0
    
    def _check_data_attributes(self, attributes):
        """Проверка data атрибутов"""
        for attr_name, attr_value in attributes.items():
            if attr_name.startswith('data-') and any(ad_attr in attr_name for ad_attr in AdPatterns.AD_DATA_ATTRIBUTES):
                return 0.9
                
        return 0.0
    
    def _check_other_attributes(self, attributes):
        """Проверка других атрибутов"""
        score = 0.0
        
        # Проверка src атрибута
        src = attributes.get('src', '').lower()
        if src and any(network in src for network in ['ad', 'banner', 'ads']):
            score = max(score, 0.6)
        
        # Проверка href атрибута
        href = attributes.get('href', '').lower()
        if href and any(keyword in href for keyword in AdPatterns.AD_KEYWORDS):
            score = max(score, 0.5)
        
        return score