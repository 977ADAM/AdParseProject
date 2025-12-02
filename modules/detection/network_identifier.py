import re
import logging
from config.ad_patterns import AdPatterns

class NetworkIdentifier:
    """Класс для идентификации рекламных сетей"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def identify_by_domain(self, url):
        """Идентификация рекламной сети по домену"""
        if not url:
            return None
        
        for network, domains in AdPatterns.AD_NETWORKS.items():
            for domain in domains:
                if re.search(domain, url, re.IGNORECASE):
                    confidence = 0.9 if network in ['yandex_ads'] else 0.8
                    return {
                        'network': network,
                        'confidence': confidence,
                        'matched_domain': domain
                    }
        
        return None
    
    def identify_by_content(self, content):
        """Идентификация по содержимому скрипта"""
        if not content:
            return None
            
        content_lower = content.lower()
        
        for pattern in AdPatterns.AD_SCRIPT_PATTERNS:
            if pattern in content_lower:
                network = self._map_script_to_network(pattern)
                return {
                    'network': network,
                    'confidence': 0.7,
                    'matched_pattern': pattern
                }
        
        return None
    
    def identify_by_attributes(self, attributes):
        """Идентификация по атрибутам элемента"""
        class_attr: str = attributes.get('class', '')
        id_attr: str = attributes.get('id', '')
        src_attr: str = attributes.get('src', '')
        
        # Проверка на конкретные рекламные сети по классам/ID
        if re.search('adsbygoogle', class_attr, re.IGNORECASE):

            return {'network': 'google_ads', 'confidence': 0.9}
        
        elif re.search('yandex_rtb_', class_attr, re.IGNORECASE) or \
            re.search('yandex_rtb_', id_attr, re.IGNORECASE) or \
            re.search('adfox_', id_attr, re.IGNORECASE) or \
            re.search('adfox_', id_attr, re.IGNORECASE):

            return {'network': 'yandex_ads', 'confidence': 0.9}
        
        elif re.search('fb-ad', class_attr, re.IGNORECASE):

            return {'network': 'meta_ads', 'confidence': 0.8}
        
        # Проверка по src
        if src_attr:
            network_info = self.identify_by_domain(src_attr)
            if network_info:
                return network_info
        
        return None
    
    def _map_script_to_network(self, script_pattern):
        """Сопоставление паттерна скрипта с рекламной сетью"""
        mapping = {
            'googletag': 'google_ads',
            'google_ad': 'google_ads',
            'adsbygoogle': 'google_ads',
            'yaContext': 'yandex_ads',
            'yandexContext': 'yandex_ads',
            'adfox': 'yandex_ads',
            'fbq': 'meta_ads',
            'facebook-pixel': 'meta_ads',
            'ttq': 'tiktok_ads',
            'tiktok-pixel': 'tiktok_ads',
            'amazon-adsystem': 'amazon_ads',
            'taboola': 'taboola',
            'outbrain': 'outbrain',
            'revcontent': 'revcontent',
            'criteo': 'criteo'
        }
        
        for pattern, network in mapping.items():
            if pattern in script_pattern:
                return network
        
        return 'unknown_network'