from urllib.parse import urlparse
from typing import List, Optional
import logging

class URLValidator:
    logger = logging.getLogger(__name__)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            URLValidator.logger.warning(f"Invalid URL {url}: {e}")
            return False
    
    @staticmethod
    def normalize_url(url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    @staticmethod
    def extract_domain(url, compare_url=None):
        try:
            parsed = urlparse(url)
            domain = parsed.hostname
            if ':' in domain:
                domain = domain.split(':')[0]

            if compare_url:
                compare_parsed = urlparse(compare_url)
                compare_domain = compare_parsed.hostname
                if ':' in compare_domain:
                    compare_domain = compare_domain.split(':')[0]
                return domain == compare_domain
            else:
                return domain
            
        except Exception as e:
            URLValidator.logger.warning(f"Ошибка извлечения домена из {url}: {e}")
            return None