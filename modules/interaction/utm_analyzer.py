import logging
import re
from urllib.parse import urlparse, parse_qs, unquote

class UTMAnalyzer:
    """Простой анализатор UTM параметров"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_utm_params(self, url):
        """
        Извлечение UTM параметров из URL
        
        Args:
            url: URL для анализа
            
        Returns:
            dict: UTM параметры
        """
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            utm_params = {}
            standard_utm = [
                'utm_source', 'utm_medium', 'utm_campaign',
                'utm_term', 'utm_content', 'utm_id'
            ]
            
            for key, value in query_params.items():
                if key in standard_utm:
                    utm_params[key] = unquote(value[0]) if value else ''
                elif key.startswith('utm_'):
                    utm_params[key] = unquote(value[0]) if value else ''
            
            return utm_params
            
        except Exception as e:
            self.logger.error(f"Error extracting UTM params: {str(e)}")
            return {}
    
    def analyze_utm_completeness(self, utm_params):
        """
        Анализ полноты UTM параметров
        
        Args:
            utm_params: Словарь UTM параметров
            
        Returns:
            dict: Анализ полноты
        """
        essential = ['utm_source', 'utm_medium', 'utm_campaign']
        present = [key for key in essential if key in utm_params]
        
        return {
            'has_utm': len(utm_params) > 0,
            'total_utm_params': len(utm_params),
            'essential_params_present': len(present),
            'missing_essential': [key for key in essential if key not in utm_params],
            'completeness_score': (len(present) / len(essential)) * 100 if essential else 0
        }
    
    def generate_utm_report(self, url):
        """
        Генерация простого отчета по UTM параметрам
        
        Args:
            url: URL для анализа
            
        Returns:
            dict: Отчет по UTM
        """
        utm_params = self.extract_utm_params(url)
        completeness = self.analyze_utm_completeness(utm_params)
        
        return {
            'url': url,
            'utm_params': utm_params,
            'completeness': completeness,
            'recommendations': self._generate_recommendations(completeness)
        }
    
    def _generate_recommendations(self, completeness):
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        if not completeness['has_utm']:
            recommendations.append("No UTM parameters found. Consider adding them for better tracking.")
        
        if completeness['missing_essential']:
            missing = ', '.join(completeness['missing_essential'])
            recommendations.append(f"Missing essential UTM parameters: {missing}")
        
        if completeness['completeness_score'] == 100:
            recommendations.append("UTM parameters are complete. Good for campaign tracking.")
        
        return recommendations