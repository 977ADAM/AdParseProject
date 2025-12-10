import logging
import sys
from pathlib import Path
from config.settings import Settings

def setup_logging():
    """Настройка логирования для всего приложения"""
    
    log_dir = Settings.LOG_DIR
    log_file = log_dir / "ad_parser.log"
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Хендлер для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Уменьшаем verbosity для некоторых библиотек
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('webdriver_manager').setLevel(logging.WARNING)