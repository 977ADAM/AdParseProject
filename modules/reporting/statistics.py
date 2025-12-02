import logging
from collections import Counter
from typing import Dict, List, Any
import statistics

class StatisticsCalculator:
    """Класс для расчета статистики по данным сканирования"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_comprehensive_stats(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Расчет комплексной статистики по сканированию
        
        Args:
            scan_data (dict): Данные сканирования
            
        Returns:
            dict: Комплексная статистика
        """
        try:
            detected_ads = scan_data.get('detected_ads', [])
            interaction_results = scan_data.get('interaction_results', [])
            
            stats = {
                'ads_statistics': self._calculate_ads_statistics(detected_ads),
                'interaction_statistics': self._calculate_interaction_statistics(interaction_results),
                'network_analysis': self._calculate_network_analysis(detected_ads),
                'performance_metrics': self._calculate_performance_metrics(scan_data),
                'quality_metrics': self._calculate_quality_metrics(detected_ads)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive stats: {str(e)}")
            return {}
    
    def _calculate_ads_statistics(self, ads_data: List[Dict]) -> Dict[str, Any]:
        """Расчет статистики по рекламным блокам"""
        if not ads_data:
            return {'total_ads': 0}
        
        # Размеры рекламных блоков
        widths = [ad.get('size', {}).get('width', 0) for ad in ads_data]
        heights = [ad.get('size', {}).get('height', 0) for ad in ads_data]
        areas = [w * h for w, h in zip(widths, heights)]
        
        # Confidence scores
        confidences = [ad.get('confidence', 0) for ad in ads_data]
        
        return {
            'total_ads': len(ads_data),
            'size_stats': {
                'avg_width': statistics.mean(widths) if widths else 0,
                'avg_height': statistics.mean(heights) if heights else 0,
                'avg_area': statistics.mean(areas) if areas else 0,
                'min_size': min(areas) if areas else 0,
                'max_size': max(areas) if areas else 0
            },
            'confidence_stats': {
                'average': statistics.mean(confidences) if confidences else 0,
                'median': statistics.median(confidences) if confidences else 0,
                'std_dev': statistics.stdev(confidences) if len(confidences) > 1 else 0,
                'min': min(confidences) if confidences else 0,
                'max': max(confidences) if confidences else 0
            }
        }
    
    def _calculate_interaction_statistics(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Расчет статистики по взаимодействиям"""
        if not interaction_data:
            return {'total_interactions': 0}
        
        success_rates = [
            interaction.get('summary', {}).get('success_rate', 0)
            for interaction in interaction_data
        ]
        
        successful_attempts = [
            interaction.get('summary', {}).get('successful_attempts', 0)
            for interaction in interaction_data
        ]
        
        return {
            'total_interactions': len(interaction_data),
            'success_rate_stats': {
                'average': statistics.mean(success_rates) if success_rates else 0,
                'median': statistics.median(success_rates) if success_rates else 0,
                'successful_interactions': sum(successful_attempts)
            },
            'redirect_analysis': self._analyze_redirect_patterns(interaction_data)
        }
    
    def _analyze_redirect_patterns(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Анализ паттернов редиректов"""
        redirect_types = []
        for interaction in interaction_data:
            redirect_types.extend(
                interaction.get('summary', {}).get('redirect_types', [])
            )
        
        redirect_counter = Counter(redirect_types)
        
        return {
            'total_redirects': len(redirect_types),
            'redirect_type_distribution': dict(redirect_counter),
            'most_common_redirect': redirect_counter.most_common(1)[0] if redirect_counter else None
        }
    
    def _calculate_network_analysis(self, ads_data: List[Dict]) -> Dict[str, Any]:
        """Анализ рекламных сетей"""
        networks = [ad.get('network', 'unknown') for ad in ads_data]
        network_counter = Counter(networks)
        
        return {
            'total_networks': len(set(networks)),
            'network_distribution': dict(network_counter),
            'dominant_network': network_counter.most_common(1)[0] if network_counter else None,
            'network_diversity_index': len(set(networks)) / len(networks) if networks else 0
        }
    
    def _calculate_performance_metrics(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Расчет метрик производительности"""
        # Здесь можно добавить реальные метрики производительности
        return {
            'estimated_scan_duration': scan_data.get('scan_duration', 'N/A'),
            'ads_per_second': len(scan_data.get('detected_ads', [])) / 60,  # Примерная метрика
            'memory_usage': scan_data.get('memory_usage', 'N/A')
        }
    
    def _calculate_quality_metrics(self, ads_data: List[Dict]) -> Dict[str, Any]:
        """Расчет метрик качества обнаружения"""
        if not ads_data:
            return {'total_ads': 0}
        
        confidences = [ad.get('confidence', 0) for ad in ads_data]
        high_confidence_ads = [c for c in confidences if c > 0.7]
        medium_confidence_ads = [c for c in confidences if 0.4 <= c <= 0.7]
        low_confidence_ads = [c for c in confidences if c < 0.4]
        
        return {
            'high_confidence_ratio': len(high_confidence_ads) / len(confidences) if confidences else 0,
            'medium_confidence_ratio': len(medium_confidence_ads) / len(confidences) if confidences else 0,
            'low_confidence_ratio': len(low_confidence_ads) / len(confidences) if confidences else 0,
            'detection_quality_score': statistics.mean(confidences) if confidences else 0
        }
    
    def calculate_network_distribution(self, ads_data: List[Dict]) -> Dict[str, int]:
        """Расчет распределения по сетям"""
        networks = [ad.get('network', 'unknown') for ad in ads_data]
        return dict(Counter(networks))
    
    def calculate_type_distribution(self, ads_data: List[Dict]) -> Dict[str, int]:
        """Расчет распределения по типам"""
        types = [ad.get('type', 'unknown') for ad in ads_data]
        return dict(Counter(types))
    
    def calculate_confidence_stats(self, ads_data: List[Dict]) -> Dict[str, float]:
        """Расчет статистики confidence"""
        confidences = [ad.get('confidence', 0) for ad in ads_data]
        if not confidences:
            return {}
        
        return {
            'mean': statistics.mean(confidences),
            'median': statistics.median(confidences),
            'std_dev': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'min': min(confidences),
            'max': max(confidences)
        }
    
    def calculate_comparative_stats(self, multiple_scan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Расчет сравнительной статистики по множественным сканированиям
        
        Args:
            multiple_scan_data (list): Данные множественных сканирований
            
        Returns:
            dict: Сравнительная статистика
        """
        try:
            comparative_stats = {
                'scan_comparison': [],
                'trends_analysis': self._analyze_trends(multiple_scan_data),
                'performance_comparison': self._compare_performance(multiple_scan_data)
            }
            
            for scan_data in multiple_scan_data:
                scan_stats = {
                    'domain': scan_data.get('main_domain', 'unknown'),
                    'total_ads': len(scan_data.get('detected_ads', [])),
                    'avg_confidence': self.calculate_confidence_stats(
                        scan_data.get('detected_ads', [])
                    ).get('mean', 0),
                    'networks_found': len(self.calculate_network_distribution(
                        scan_data.get('detected_ads', [])
                    )),
                    'interaction_success_rate': self._calculate_interaction_statistics(
                        scan_data.get('interaction_results', [])
                    ).get('success_rate_stats', {}).get('average', 0)
                }
                comparative_stats['scan_comparison'].append(scan_stats)
            
            return comparative_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating comparative stats: {str(e)}")
            return {}
    
    def _analyze_trends(self, multiple_scan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ трендов по множественным сканированиям"""
        # Здесь можно реализовать анализ трендов
        return {
            'total_ads_trend': 'stable',  # Пример: increasing, decreasing, stable
            'network_diversity_trend': 'stable',
            'confidence_trend': 'stable'
        }
    
    def _compare_performance(self, multiple_scan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Сравнение производительности сканирований"""
        # Здесь можно реализовать сравнение производительности
        return {
            'fastest_scan': 'N/A',
            'slowest_scan': 'N/A',
            'average_duration': 'N/A'
        }