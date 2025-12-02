import csv
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class CSVExporter:
    """Класс для экспорта отчетов в CSV формате"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.reports_dir = config.OUTPUT_DIR / "reports"
    
    def export_report(self, report_data: Dict[str, Any], filename: str) -> str:
        """
        Экспорт отчета в CSV формате
        
        Args:
            report_data (dict): Данные отчета
            filename (str): Имя файла
            
        Returns:
            str: Путь к сохраненному файлу
        """
        try:
            file_path = self.reports_dir / filename
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Запись основной информации
                self._write_summary_section(writer, report_data)
                writer.writerow([])
                
                # Запись данных о рекламе
                self._write_ads_section(writer, report_data)
                writer.writerow([])
                
                # Запись данных о взаимодействиях
                self._write_interactions_section(writer, report_data)
                writer.writerow([])
                
                # Запись статистики
                self._write_statistics_section(writer, report_data)
            
            self.logger.info(f"CSV report exported: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV report: {str(e)}")
            return ""
    
    def _write_summary_section(self, writer, report_data: Dict[str, Any]):
        """Запись раздела сводки"""
        writer.writerow(['=== AD DETECTION REPORT SUMMARY ==='])
        writer.writerow(['Generated at', report_data.get('metadata', {}).get('generated_at', 'N/A')])
        
        scan_summary = report_data.get('scan_summary', {})
        writer.writerow(['URLs Processed', scan_summary.get('total_urls_processed', 0)])
        writer.writerow(['Ads Detected', scan_summary.get('total_ads_detected', 0)])
        writer.writerow(['Successful Interactions', scan_summary.get('successful_interactions', 0)])
    
    def _write_ads_section(self, writer, report_data: Dict[str, Any]):
        """Запись раздела рекламы"""
        writer.writerow(['=== DETECTED ADS ==='])
        writer.writerow(['ID', 'Type', 'Network', 'Confidence', 'Width', 'Height', 'Method'])
        
        ads_data = report_data.get('ads_detection', {}).get('ads', [])
        for ad in ads_data:
            size = ad.get('size', {})
            writer.writerow([
                ad.get('id', 'N/A'),
                ad.get('type', 'unknown'),
                ad.get('network', 'unknown'),
                f"{ad.get('confidence', 0):.2f}",
                size.get('width', 0),
                size.get('height', 0),
                ad.get('detection_method', 'unknown')
            ])
    
    def _write_interactions_section(self, writer, report_data: Dict[str, Any]):
        """Запись раздела взаимодействий"""
        writer.writerow(['=== INTERACTIONS ==='])
        writer.writerow(['Ad ID', 'Network', 'Success Rate', 'Redirect Types', 'UTM Found'])
        
        interactions_data = report_data.get('interaction_results', {}).get('interactions', [])
        for interaction in interactions_data:
            redirect_types = ', '.join(interaction.get('redirect_types', []))
            writer.writerow([
                interaction.get('ad_id', 'N/A'),
                interaction.get('ad_network', 'unknown'),
                f"{interaction.get('success_rate', 0):.1f}%",
                redirect_types,
                'Yes' if interaction.get('utm_found') else 'No'
            ])
    
    def _write_statistics_section(self, writer, report_data: Dict[str, Any]):
        """Запись раздела статистики"""
        writer.writerow(['=== STATISTICS ==='])
        
        stats = report_data.get('statistics', {})
        ads_stats = stats.get('ads_statistics', {})
        
        writer.writerow(['Total Ads', ads_stats.get('total_ads', 0)])
        writer.writerow(['Average Confidence', f"{ads_stats.get('confidence_stats', {}).get('average', 0):.2f}"])
        
        network_stats = stats.get('network_analysis', {})
        writer.writerow(['Networks Found', network_stats.get('total_networks', 0)])
    
    def export_batch_report(self, batch_data: Dict[str, Any], filename: str) -> str:
        """
        Экспорт batch отчета в CSV формате
        
        Args:
            batch_data (dict): Данные batch отчета
            filename (str): Имя файла
            
        Returns:
            str: Путь к сохраненному файлу
        """
        try:
            file_path = self.reports_dir / filename
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Запись сводки batch
                self._write_batch_summary(writer, batch_data)
                writer.writerow([])
                
                # Запись сравнительного анализа
                self._write_comparative_analysis(writer, batch_data)
                writer.writerow([])
                
                # Запись данных по отдельным сканированиям
                self._write_individual_scans(writer, batch_data)
            
            self.logger.info(f"CSV batch report exported: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV batch report: {str(e)}")
            return ""
    
    def _write_batch_summary(self, writer, batch_data: Dict[str, Any]):
        """Запись сводки batch отчета"""
        writer.writerow(['=== BATCH REPORT SUMMARY ==='])
        
        batch_summary = batch_data.get('batch_summary', {})
        writer.writerow(['Total Scans', batch_summary.get('total_scans', 0)])
        writer.writerow(['Total URLs', batch_summary.get('total_urls_processed', 0)])
        writer.writerow(['Total Ads', batch_summary.get('total_ads_detected', 0)])
        writer.writerow(['Domains Covered', ', '.join(batch_summary.get('domains_covered', []))])
    
    def _write_comparative_analysis(self, writer, batch_data: Dict[str, Any]):
        """Запись сравнительного анализа"""
        writer.writerow(['=== COMPARATIVE ANALYSIS ==='])
        writer.writerow(['Domain', 'Total Ads', 'Avg Confidence', 'Networks', 'Success Rate'])
        
        comparative_stats = batch_data.get('comparative_analysis', {})
        scan_comparison = comparative_stats.get('scan_comparison', [])
        
        for scan in scan_comparison:
            writer.writerow([
                scan.get('domain', 'unknown'),
                scan.get('total_ads', 0),
                f"{scan.get('avg_confidence', 0):.2f}",
                scan.get('networks_found', 0),
                f"{scan.get('interaction_success_rate', 0):.1f}%"
            ])
    
    def _write_individual_scans(self, writer, batch_data: Dict[str, Any]):
        """Запись данных по отдельным сканированиям"""
        writer.writerow(['=== INDIVIDUAL SCANS ==='])
        
        individual_reports = batch_data.get('individual_reports', [])
        for i, report in enumerate(individual_reports):
            writer.writerow([f'Scan {i+1}'])
            
            scan_summary = report.get('scan_summary', {})
            writer.writerow(['URLs Processed', scan_summary.get('total_urls_processed', 0)])
            writer.writerow(['Ads Detected', scan_summary.get('total_ads_detected', 0)])
            writer.writerow([])