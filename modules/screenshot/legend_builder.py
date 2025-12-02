import logging
from PIL import Image, ImageDraw

class LegendBuilder:
    """Класс для построения детализированных легенд и отчетов"""
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def create_detailed_legend_image(self, ads_data, output_path=None):
        """Создание детализированного изображения с информацией о рекламных блоках"""
        try:
            width = 600
            line_height = 25
            padding = 20
            
            height = padding * 2 + (len(ads_data) + 2) * line_height
            
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            title = "Ad Detection Report"
            draw.text((padding, padding), title, fill=(0, 0, 0))
            
            y_position = padding + line_height * 1.5
            
            headers = ["#", "Network", "Type", "Size", "Confidence", "Method"]
            header_x = padding
            col_width = (width - padding * 2) // len(headers)
            
            for i, header in enumerate(headers):
                draw.text((header_x + i * col_width, y_position), header, fill=(0, 0, 0))
            
            y_position += line_height
            
            for i, ad in enumerate(ads_data):
                row_y = y_position + i * line_height
                
                draw.text((padding, row_y), str(i+1), fill=(0, 0, 0))
                
                network = ad.get('network', 'unknown')
                draw.text((padding + col_width, row_y), network, fill=(0, 0, 0))
                
                ad_type = ad.get('type', 'unknown')
                draw.text((padding + col_width * 2, row_y), ad_type, fill=(0, 0, 0))
                
                size = ad.get('size', {})
                size_str = f"{size.get('width', 0)}x{size.get('height', 0)}"
                draw.text((padding + col_width * 3, row_y), size_str, fill=(0, 0, 0))
                
                confidence = ad.get('confidence', 0)
                confidence_str = f"{confidence:.2f}"
                confidence_color = (0, 128, 0) if confidence > 0.7 else (255, 165, 0) if confidence > 0.4 else (255, 0, 0)
                draw.text((padding + col_width * 4, row_y), confidence_str, fill=confidence_color)
                
                method = ad.get('detection_method', 'unknown')
                draw.text((padding + col_width * 5, row_y), method, fill=(0, 0, 0))
            
            if output_path is None:
                output_path = self.config.SCREENSHOT_DIR / "ad_detection_legend.png"
            
            image.save(output_path)
            self.logger.info(f"Detailed legend saved: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating detailed legend: {str(e)}")
            return None
    
    def create_summary_statistics(self, ads_data):
        """Создание статистики обнаружения рекламы"""
        stats = {
            'total_ads': len(ads_data),
            'networks': {},
            'types': {},
            'confidence_distribution': {
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'size_categories': {},
            'detection_methods': {}
        }
        
        for ad in ads_data:
            network = ad.get('network', 'unknown')
            stats['networks'][network] = stats['networks'].get(network, 0) + 1
            
            ad_type = ad.get('type', 'unknown')
            stats['types'][ad_type] = stats['types'].get(ad_type, 0) + 1
            
            confidence = ad.get('confidence', 0)
            if confidence > 0.7:
                stats['confidence_distribution']['high'] += 1
            elif confidence > 0.4:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
            
            method = ad.get('detection_method', 'unknown')
            stats['detection_methods'][method] = stats['detection_methods'].get(method, 0) + 1
            
            size = ad.get('size', {})
            width = size.get('width', 0)
            height = size.get('height', 0)
            area = width * height
            
            if area < 10000:
                category = 'very_small'
            elif area < 50000:
                category = 'small'
            elif area < 200000:
                category = 'medium'
            else:
                category = 'large'
            
            stats['size_categories'][category] = stats['size_categories'].get(category, 0) + 1
        
        return stats