from selenium.webdriver.chrome.options import Options
from .settings import Settings

class BrowserConfig:
    @staticmethod
    def get_chrome_options(config: Settings):
        options = Options()

        if config.HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={config.WIDTH_WINDOW},{config.HEIGHT_WINDOW}")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=1024")
        
        return options
    