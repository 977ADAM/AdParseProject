import psutil
import logging
import gc

class MemoryManager:
    """Менеджер для мониторинга и управления потреблением памяти"""
    
    def __init__(self, memory_limit_mb=1000):
        self.memory_limit = memory_limit_mb
        self.logger = logging.getLogger(__name__)
    
    def check_memory(self):
        """
        Проверяет текущее потребление памяти
        
        Returns:
            bool: True если память в пределах лимита, False если接近 лимита
        """
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        self.logger.debug(f"Current memory usage: {memory_mb:.2f} MB / {self.memory_limit} MB")
        
        # Возвращаем False если используем больше 80% лимита
        return memory_mb < (self.memory_limit * 0.8)
    
    def force_cleanup(self):
        """Принудительная очистка памяти"""
        self.logger.info("Performing memory cleanup...")
        gc.collect()
        
        # Дополнительные методы очистки если нужно
        if hasattr(gc, 'get_referrers'):
            gc.collect(2)
    
    def get_memory_usage(self):
        """Возвращает текущее использование памяти в MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024