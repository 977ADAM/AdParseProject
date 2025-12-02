import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from config.settings import Settings

class JSONExporter:
    """Класс для экспорта отчетов в JSON формате"""
    
    def __init__(self, config: Settings):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.reports_dir = config.OUTPUT_DIR / "reports"
    
    def export_report(self, report_data: Dict[str, Any], filename: str) -> str:
        """Экспорт отчета в JSON формате"""
        try:
            file_path = self.reports_dir / filename
            
            export_metadata = {
                'exported_at': datetime.now().isoformat(),
                'export_format': 'JSON',
                'export_version': '1.0'
            }
            
            report_data['export_metadata'] = export_metadata
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON report exported: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON report: {str(e)}")
            return ""
    
    def export_batch_report(self, batch_data: Dict[str, Any], filename: str) -> str:
        """
        Экспорт batch отчета в JSON формате
        
        Args:
            batch_data (dict): Данные batch отчета
            filename (str): Имя файла
            
        Returns:
            str: Путь к сохраненному файлу
        """
        try:
            file_path = self.reports_dir / filename
            
            # Добавление метаданных экспорта
            export_metadata = {
                'exported_at': datetime.now().isoformat(),
                'export_format': 'JSON',
                'export_type': 'batch',
                'export_version': '1.0'
            }
            
            batch_data['export_metadata'] = export_metadata
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON batch report exported: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON batch report: {str(e)}")
            return ""