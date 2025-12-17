from pathlib import Path

class Settings:
    """Основные настройки приложения"""

    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
    LOG_DIR = OUTPUT_DIR / "logs"
    COOKIES_DIR = OUTPUT_DIR / "cookies"
    
    for directory in [OUTPUT_DIR, SCREENSHOT_DIR, LOG_DIR, COOKIES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    WIDTH_WINDOW = 1920
    HEIGHT_WINDOW = 1080
    BROWSER = "chrome"
    HEADLESS = True
    PAGE_LOAD_TIMEOUT = 30
    IMPLICIT_WAIT = 5
    
    MEMORY_LIMIT_MB = 1000
    CLEANUP_INTERVAL = 50
    
    DISABLE_IMAGES = True
    MAX_RETRIES = 3
    RETRY_DELAY = 2