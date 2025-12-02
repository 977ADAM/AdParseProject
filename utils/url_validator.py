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
    def normalize_urls(urls: List[str]) -> List[str]:
        valid_urls = []
        for url in urls:
            if URLValidator.is_valid_url(url):
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                valid_urls.append(url)
            else:
                URLValidator.logger.warning(f"Skipping invalid URL: {url}")
        
        return valid_urls
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            URLValidator.logger.warning(f"Ошибка извлечения домена из {url}: {e}")
            return None