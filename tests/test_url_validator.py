import pytest
from utils.url_validator import URLValidator

class TestURLValidator:
    """Тесты для валидатора URL"""
    
    def setup_method(self):
        self.validator = URLValidator()
    
    def test_validate_valid_url(self):
        """Тест валидации корректного URL"""
        valid_urls = [
            "https://www.google.com",
            "http://example.com",
            "https://example.com/path?query=value",
            "https://sub.domain.co.uk"
        ]
        
        for url in valid_urls:
            assert self.validator.is_valid_url(url) == True
    
    def test_validate_invalid_url(self):
        """Тест валидации некорректного URL"""
        invalid_urls = [
            "not-a-url",
            "http:example.com",
            "ftp:example.com",
            "://example.com",
        ]
        
        for url in invalid_urls:
            assert self.validator.is_valid_url(url) == False
    
    def test_normalize_url(self):
        """Тест нормализации URL"""
        test_cases = [
            ("google.com", "https://google.com"),
            ("www.m24.ru", "https://www.m24.ru"),
            ("ria.ru", "https://ria.ru")
        ]
        
        for input_url, expected in test_cases:
            normalized = self.validator.normalize_urls(input_url)
            assert normalized == expected
    
    def test_extract_domain(self):
        """Тест извлечения домена"""
        test_cases = [
            ("https://www.google.com/search", "www.google.com"),
            ("http://example.com:8080/path", "example.com"),
            ("https://sub.domain.co.uk/page", "sub.domain.co.uk")
        ]
        
        for url, expected_domain in test_cases:
            domain = self.validator.extract_domain(url)
            assert domain == expected_domain
    
    def test_is_same_domain(self):
        """Тест проверки одинаковых доменов"""
        assert self.validator.extract_domain(
            "https://www.google.com/search",
            "http://www.google.com/maps"
        ) == True
        
        assert self.validator.extract_domain(
            "https://google.com",
            "https://example.com"
        ) == False