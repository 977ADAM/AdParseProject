import logging
from config.ad_patterns import AdPatterns

class SizeAnalyzer:
    """Класс для анализа размеров элементов на соответствие рекламным стандартам"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_standard_ad_size(self, width, height, tolerance=5):
        """
        Проверка соответствия размера стандартам рекламы
        
        Args:
            width (int): Ширина элемента
            height (int): Высота элемента
            tolerance (int): Допустимое отклонение в пикселях
            
        Returns:
            str or None: Название стандартного размера или None
        """
        for std_width, std_height in AdPatterns.STANDARD_AD_SIZES:
            if (abs(width - std_width) <= tolerance and 
                abs(height - std_height) <= tolerance):
                return f"{std_width}x{std_height}"
        
        return None
    
    def get_size_category(self, width, height):
        """
        Определение категории размера
        
        Args:
            width (int): Ширина
            height (int): Высота
            
        Returns:
            str: Категория размера
        """
        area = width * height
        
        if area < 10000:  # 100x100
            return 'very_small'
        elif area < 25000:  # ~158x158
            return 'small'
        elif area < 75000:  # ~274x274
            return 'medium'
        elif area < 200000:  # ~447x447
            return 'large'
        else:
            return 'very_large'
    
    def is_suspicious_size(self, width, height):
        """
        Проверка на подозрительные размеры (может быть реклама)
        
        Args:
            width (int): Ширина
            height (int): Высота
            
        Returns:
            bool: Является ли размер подозрительным
        """
        # Очень узкие или очень широкие элементы
        if height > 0:
            ratio = width / height
            if ratio > 10 or ratio < 0.1:  # Очень широкий или очень узкий
                return True
        
        # Очень маленькие или очень большие элементы
        area = width * height
        if area < 100 or area > 1000000:  # 1x100 или 1000x1000
            return True
            
        return False