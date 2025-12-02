import logging
from config.settings import Settings
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

class ScreenshotAnnotator:
    """Класс для добавления аннотаций на скриншоты"""
    
    def __init__(self, config: Settings):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.colors = self._initialize_colors()
        self.fonts = self._initialize_fonts()
    
    def _initialize_colors(self):
        """Инициализация цветовой палитры для аннотаций"""
        return {
            'google_ads': (255, 0, 0, 180),      # Красный
            'yandex_ads': (0, 0, 255, 180),      # Синий
            'meta_ads': (0, 128, 0, 180),        # Зеленый
            'tiktok_ads': (0, 0, 0, 180),        # Черный
            'amazon_ads': (255, 165, 0, 180),    # Оранжевый
            'unknown': (128, 0, 128, 180),       # Фиолетовый
            'text': (255, 255, 255, 255),        # Белый для текста
            'background': (0, 0, 0, 180)         # Черный для фона текста
        }
    
    def _initialize_fonts(self):
        """Инициализация шрифтов"""
        fonts = {}
        try:
            # Попытка загрузить стандартные шрифты
            fonts['large'] = ImageFont.truetype("arial.ttf", 16)
            fonts['medium'] = ImageFont.truetype("arial.ttf", 14)
            fonts['small'] = ImageFont.truetype("arial.ttf", 12)
        except:
            # Fallback на базовый шрифт
            fonts['large'] = ImageFont.load_default()
            fonts['medium'] = ImageFont.load_default()
            fonts['small'] = ImageFont.load_default()
            self.logger.warning("Using default font - arial.ttf not available")
        
        return fonts
    
    def annotate_ads_on_screenshot(self, screenshot_path, ads_data, output_path=None):
        """Добавление аннотаций рекламных блоков на скриншот"""
        try:
            image = Image.open(screenshot_path)
            draw = ImageDraw.Draw(image, 'RGBA')
            
            for ad in ads_data:
                self._annotate_ad(draw, ad, image.size)
            
            self._add_legend(draw, ads_data, image.size)
            
            self._add_title(draw, f"Detected Ads: {len(ads_data)}", image.size)
            
            if output_path is None:
                original_path = Path(screenshot_path)
                output_path = original_path.parent / f"annotated_{original_path.name}"
            
            image.save(output_path, quality=95)
            self.logger.info(f"Annotated screenshot saved: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error annotating screenshot: {str(e)}")
            return None
    
    def _annotate_ad(self, draw, ad, image_size):
        """Добавление аннотации для одного рекламного блока"""
        try:
            ad_number = ad.get('id')
            location = ad.get('location', {})
            size = ad.get('size', {})
            network = ad.get('network', 'unknown')
            confidence = ad.get('confidence', 0)

            
            x, y = location.get('x', 0), location.get('y', 0)
            width, height = size.get('width', 0), size.get('height', 0)
            
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                return
            
            color = self.colors.get(network, self.colors['unknown'])
            
            self._draw_bounding_box(draw, x, y, width, height, color, ad_number)
            
            self._draw_ad_label(draw, x, y, width, height, ad_number, network, confidence, color)
            
        except Exception as e:
            self.logger.debug(f"Error annotating ad {ad_number}: {str(e)}")
    
    def _draw_bounding_box(self, draw, x, y, width, height, color, ad_number):
        """Рисование ограничивающей рамки"""
        # Основная рамка
        draw.rectangle([x, y, x + width, y + height], outline=color, width=3)
        
        # Угловые маркеры
        marker_size = 10
        # Левый верхний
        draw.rectangle([x, y, x + marker_size, y + marker_size], fill=color)
        # Правый верхний
        draw.rectangle([x + width - marker_size, y, x + width, y + marker_size], fill=color)
        # Левый нижний
        draw.rectangle([x, y + height - marker_size, x + marker_size, y + height], fill=color)
        # Правый нижний
        draw.rectangle([x + width - marker_size, y + height - marker_size, x + width, y + height], fill=color)
    
    def _draw_ad_label(self, draw, x, y, width, height, ad_number, network, confidence, color):
        """Добавление текстовой метки"""
        label_text = f"{ad_number}. {network} ({confidence:.1f})"
        
        # Расчет позиции метки
        text_bbox = draw.textbbox((0, 0), label_text, font=self.fonts['small'])
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Позиционирование метки
        label_x = x
        label_y = y - text_height - 5
        
        # Если метка выходит за верхнюю границу, размещаем внутри блока
        if label_y < 0:
            label_y = y + 5
        
        # Фон для текста
        padding = 5
        draw.rectangle([
            label_x - padding,
            label_y - padding,
            label_x + text_width + padding,
            label_y + text_height + padding
        ], fill=self.colors['background'])
        
        # Текст
        draw.text((label_x, label_y), label_text, fill=self.colors['text'], font=self.fonts['small'])
    
    def _add_legend(self, draw, ads_data, image_size):
        """Добавление легенды на скриншот"""
        try:
            legend_x = 20
            legend_y = image_size[1] - 150  # Отступ от низа
            
            # Фон легенды
            draw.rectangle([
                legend_x - 10, legend_y - 10,
                legend_x + 200, legend_y + 120
            ], fill=(255, 255, 255, 220))
            
            # Заголовок легенды
            draw.text((legend_x, legend_y), "Ad Networks Legend:", 
                     fill=(0, 0, 0, 255), font=self.fonts['medium'])
            
            legend_y += 25
            
            # Сбор уникальных сетей
            networks = {}
            for ad in ads_data:
                network = ad.get('network', 'unknown')
                if network not in networks:
                    networks[network] = self.colors.get(network, self.colors['unknown'])
            
            # Ограничение количества элементов в легенде
            networks = dict(list(networks.items())[:6])
            
            # Элементы легенды
            for i, (network, color) in enumerate(networks.items()):
                y_pos = legend_y + (i * 20)
                
                # Цветной квадрат
                draw.rectangle([legend_x, y_pos, legend_x + 15, y_pos + 15], fill=color)
                
                # Текст
                network_name = network.replace('_ads', '').title()
                draw.text((legend_x + 20, y_pos), network_name, 
                         fill=(0, 0, 0, 255), font=self.fonts['small'])
        
        except Exception as e:
            self.logger.debug(f"Error adding legend: {str(e)}")
    
    def _add_title(self, draw, title, image_size):
        """Добавление заголовка"""
        try:
            text_bbox = draw.textbbox((0, 0), title, font=self.fonts['large'])
            text_width = text_bbox[2] - text_bbox[0]
            
            title_x = (image_size[0] - text_width) // 2
            title_y = 10
            
            # Фон заголовка
            padding = 8
            draw.rectangle([
                title_x - padding, title_y - padding,
                title_x + text_width + padding, title_y + (text_bbox[3] - text_bbox[1]) + padding
            ], fill=(0, 0, 0, 200))
            
            # Текст заголовка
            draw.text((title_x, title_y), title, fill=self.colors['text'], font=self.fonts['large'])
            
        except Exception as e:
            self.logger.debug(f"Error adding title: {str(e)}")
    
    def create_comparison_image(self, original_path, annotated_path, output_path=None):
        """
        Создание сравнительного изображения (оригинал + аннотированный)
        
        Args:
            original_path (str): Путь к оригинальному скриншоту
            annotated_path (str): Путь к аннотированному скриншоту
            output_path (str): Путь для сохранения сравнения
            
        Returns:
            str: Путь к сравнительному изображению
        """
        try:
            original_img = Image.open(original_path)
            annotated_img = Image.open(annotated_path)
            
            # Создание нового изображения для сравнения
            comparison_width = original_img.width + annotated_img.width
            comparison_height = max(original_img.height, annotated_img.height)
            
            comparison_img = Image.new('RGB', (comparison_width, comparison_height), 'white')
            
            # Вставка изображений
            comparison_img.paste(original_img, (0, 0))
            comparison_img.paste(annotated_img, (original_img.width, 0))
            
            # Добавление подписей
            draw = ImageDraw.Draw(comparison_img)
            
            # Подпись для оригинального изображения
            orig_text = "Original"
            orig_bbox = draw.textbbox((0, 0), orig_text, font=self.fonts['medium'])
            orig_x = (original_img.width - (orig_bbox[2] - orig_bbox[0])) // 2
            draw.text((orig_x, 10), orig_text, fill=(0, 0, 0), font=self.fonts['medium'])
            
            # Подпись для аннотированного изображения
            ann_text = "Annotated (Ads Highlighted)"
            ann_bbox = draw.textbbox((0, 0), ann_text, font=self.fonts['medium'])
            ann_x = original_img.width + (annotated_img.width - (ann_bbox[2] - ann_bbox[0])) // 2
            draw.text((ann_x, 10), ann_text, fill=(0, 0, 0), font=self.fonts['medium'])
            
            # Сохранение
            if output_path is None:
                original_path_obj = Path(original_path)
                output_path = original_path_obj.parent / f"comparison_{original_path_obj.name}"
            
            comparison_img.save(output_path, quality=95)
            self.logger.info(f"Comparison image saved: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating comparison image: {str(e)}")
            return None