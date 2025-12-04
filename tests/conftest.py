"""Конфигурационный файл pytest. Определяет фикстуры и настройки для всех тестов."""
import pytest
import logging

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Настройка логирования для тестов"""
    logging.getLogger().setLevel(logging.WARNING)
    
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


@pytest.fixture
def sample_valid_urls():
    """Фикстура с примерами валидных URL"""
    return [
        "https://google.com",
        "http://example.org",
        "https://www.github.com/user/repo",
        "http://localhost:8000",
        "https://192.168.0.1:8443",
    ]


@pytest.fixture
def sample_invalid_urls():
    """Фикстура с примерами невалидных URL"""
    return [
        "not-a-url",
        "",
        "://missing-scheme.com",
        "https://",
        "http://",
        "javascript:alert(1)",
        "data:text/html,test",
    ]


@pytest.fixture
def url_validator():
    """Фикстура для создания экземпляра URLValidator"""
    from utils.url_validator import URLValidator
    return URLValidator()
