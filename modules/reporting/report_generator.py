import logging
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from config.settings import Settings
from modules.reporting.exporters.json_exporter import JSONExporter
from modules.reporting.exporters.csv_exporter import CSVExporter
from modules.reporting.exporters.pdf_exporter import PDFExporter
from modules.reporting.statistics import StatisticsCalculator

class ReportGenerator:
    """Основной класс для генерации комплексных отчетов о рекламе"""
    def __init__(self, config: Settings):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.statistics_calculator = StatisticsCalculator()
        self.json_exporter = JSONExporter(config)
        self.csv_exporter = CSVExporter(config)
        self.pdf_exporter = PDFExporter(config)
        
        self.reports_dir = config.OUTPUT_DIR / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, scan_data: Dict[str, Any]) -> Dict[str, str]:
        """Генерация комплексного отчета по всем данным сканирования"""
        try:
            self.logger.info("Начало формирования комплексного отчета")
            
            report_data = self._prepare_report_data(scan_data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_base_name = f"ad_report_{timestamp}"
            
            report_paths = {}
            
            json_report_path = self.json_exporter.export_report(
                report_data, f"{report_base_name}.json"
            )
            report_paths['json'] = json_report_path
            
            csv_report_path = self.csv_exporter.export_report(
                report_data, f"{report_base_name}.csv"
            )
            report_paths['csv'] = csv_report_path
            
            # PDF отчет
            # pdf_report_path = self.pdf_exporter.export_report(
            #     report_data, f"{report_base_name}.pdf"
            # )
            # report_paths['pdf'] = pdf_report_path
            
            # # Сводный отчет
            # summary_report_path = self._generate_summary_report(report_data, report_base_name)
            # report_paths['summary'] = summary_report_path
            
            self.logger.info(f"Reports generated successfully: {list(report_paths.keys())}")
            return report_paths
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {str(e)}")
            return {'error': str(e)}
    
    def _prepare_report_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка и обогащение данных для отчета"""
        try:
            report_data = {
                'metadata': self._generate_metadata(scan_data.get('scan_duration')),

                'scan_summary': self._generate_scan_summary(scan_data),

                # 'url_analysis': scan_data.get('url_analysis', {}),

                'ads_detection': self._process_ads_data(scan_data.get('detected_ads', [])),

                'interaction_results': self._process_interaction_data(scan_data.get('interaction_results', [])),

                'screenshots': scan_data.get('screenshots', {}),

                'statistics': self.statistics_calculator.calculate_comprehensive_stats(scan_data),

                'recommendations': self._generate_recommendations(scan_data)
            }
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Ошибка подготовки данных отчета: {str(e)}")
            return {'error': str(e)}
    
    def _generate_metadata(self, scan_duration=None) -> Dict[str, Any]:
        """Генерация метаданных отчета"""
        return {
            'generated_at': datetime.now().isoformat(),
            'report_version': '1.0',
            'tool_name': 'Advanced Ad Parser',
            'scan_duration': scan_duration or getattr(self.config, 'SCAN_DURATION', 'N/A')
        }
    
    def _generate_scan_summary(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация сводки сканирования"""
        detected_ads = scan_data.get('detected_ads', [])
        interaction_results = scan_data.get('interaction_results', [])
        
        return {
            'total_urls_processed': len(scan_data.get('processed_urls', [])),
            'total_ads_detected': len(detected_ads),
            'successful_interactions': len([
                r for r in interaction_results 
                if r.get('summary', {}).get('successful_attempts', 0) > 0
            ]),
            'scan_timestamp': datetime.now().isoformat(),
            'main_domain': scan_data.get('main_domain', 'N/A')
        }
    
    def _process_ads_data(self, ads_data: List[Dict]) -> Dict[str, Any]:
        """Обработка данных о рекламных блоках"""
        if not ads_data:
            return {'total_ads': 0}
        
        processed_ads = []
        for ad in ads_data:
            processed_ad = {
                'id': ad.get('id', 'N/A'),
                'type': ad.get('type', 'unknown'),
                'network': ad.get('network', 'unknown'),
                'confidence': ad.get('confidence', 0),
                'detection_method': ad.get('detection_method', 'unknown'),
                'element_info': ad.get('element_info', {}),
                'screenshot_path': ad.get('screenshot_path', '')
            }
            processed_ads.append(processed_ad)
        
        return {
            'total_ads': len(processed_ads),
            'ads': processed_ads,
            'networks_distribution': self.statistics_calculator.calculate_network_distribution(ads_data),
            'types_distribution': self.statistics_calculator.calculate_type_distribution(ads_data),
            'confidence_stats': self.statistics_calculator.calculate_confidence_stats(ads_data)
        }
    
    def _process_interaction_data(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Обработка данных взаимодействия"""
        if not interaction_data:
            return {'total_interactions': 0}
        
        processed_interactions = []
        
        for interaction in interaction_data:
            ad_data = interaction.get('ad_data', {})
            interactions = interaction.get('interaction', {})
            
            processed_interaction = {
                'ad_id': ad_data.get('id', 'N/A'),
                'ad_network': ad_data.get('network', 'unknown'),
                'ad_page_link': interactions.get('utm_data'),
                'url_analysis': interactions.get('current_url')
            }
            
            processed_interactions.append(processed_interaction)

        
        return {
            'total_interactions': len(processed_interactions),
            'interactions': processed_interactions
        }
    
    def _generate_recommendations(self, scan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        detected_ads = scan_data.get('detected_ads', [])
        interaction_results = scan_data.get('interaction_results', [])
        
        # Рекомендации по обнаружению рекламы
        if len(detected_ads) == 0:
            recommendations.append({
                'category': 'detection',
                'priority': 'high',
                'message': 'No ads detected. Consider adjusting detection parameters or checking if the page contains ads.',
                'suggestion': 'Review ad patterns configuration and try different detection methods.'
            })
        elif len(detected_ads) > 20:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'message': f'Large number of ads detected ({len(detected_ads)}). This may impact page performance.',
                'suggestion': 'Consider optimizing ad loading or implementing lazy loading.'
            })
        
        # Рекомендации по взаимодействию
        successful_interactions = [
            r for r in interaction_results 
            if r.get('summary', {}).get('successful_attempts', 0) > 0
        ]
        
        if successful_interactions:
            utm_found_count = sum(1 for r in successful_interactions if r.get('summary', {}).get('utm_found', False))
            if utm_found_count > 0:
                recommendations.append({
                    'category': 'analytics',
                    'priority': 'low',
                    'message': f'UTM parameters found in {utm_found_count} interactions. Good for tracking.',
                    'suggestion': 'Analyze UTM parameters for campaign optimization.'
                })
        
        # Рекомендации по безопасности
        security_issues = []
        for interaction in interaction_results:
            security_issues.extend(interaction.get('summary', {}).get('security_issues', []))
        
        if security_issues:
            high_risk_issues = [issue for issue in security_issues if issue.get('risk_score', 0) > 70]
            if high_risk_issues:
                recommendations.append({
                    'category': 'security',
                    'priority': 'high',
                    'message': f'Found {len(high_risk_issues)} high-risk security issues in ad interactions.',
                    'suggestion': 'Review ad network security and consider blocking suspicious sources.'
                })
        
        return recommendations
    
    def _generate_summary_report(self, report_data: Dict[str, Any], base_name: str) -> str:
        """
        Генерация краткого сводного отчета
        
        Args:
            report_data (dict): Данные отчета
            base_name (str): Базовое имя файла
            
        Returns:
            str: Путь к сводному отчету
        """
        try:
            summary_path = self.reports_dir / f"{base_name}_summary.txt"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=== AD DETECTION SUMMARY REPORT ===\n\n")
                
                # Основная информация
                metadata = report_data.get('metadata', {})
                f.write(f"Generated: {metadata.get('generated_at', 'N/A')}\n")
                f.write(f"Tool: {metadata.get('tool_name', 'N/A')}\n\n")
                
                # Сводка сканирования
                scan_summary = report_data.get('scan_summary', {})
                f.write("SCAN SUMMARY:\n")
                f.write(f"- URLs Processed: {scan_summary.get('total_urls_processed', 0)}\n")
                f.write(f"- Ads Detected: {scan_summary.get('total_ads_detected', 0)}\n")
                f.write(f"- Successful Interactions: {scan_summary.get('successful_interactions', 0)}\n\n")
                
                # Статистика рекламы
                ads_data = report_data.get('ads_detection', {})
                f.write("ADS STATISTICS:\n")
                f.write(f"- Total Ads: {ads_data.get('total_ads', 0)}\n")
                
                networks = ads_data.get('networks_distribution', {})
                if networks:
                    f.write("- Networks Distribution:\n")
                    for network, count in networks.items():
                        f.write(f"  * {network}: {count}\n")
                
                # Рекомендации
                recommendations = report_data.get('recommendations', [])
                if recommendations:
                    f.write("\nRECOMMENDATIONS:\n")
                    for rec in recommendations:
                        f.write(f"- [{rec.get('priority', 'medium').upper()}] {rec.get('message', '')}\n")
                
                f.write(f"\nFull reports available in: {self.reports_dir}")
            
            self.logger.info(f"Summary report generated: {summary_path}")
            return str(summary_path)
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {str(e)}")
            return ""
    
    def generate_batch_report(self, multiple_scan_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Генерация отчета по множественным сканированиям
        
        Args:
            multiple_scan_data (list): Данные множественных сканирований
            
        Returns:
            dict: Пути к сгенерированным отчетам
        """
        try:
            self.logger.info(f"Generating batch report for {len(multiple_scan_data)} scans")
            
            batch_report_data = {
                'metadata': self._generate_metadata(),
                'batch_summary': self._generate_batch_summary(multiple_scan_data),
                'individual_reports': [],
                'comparative_analysis': self.statistics_calculator.calculate_comparative_stats(multiple_scan_data)
            }
            
            # Обработка каждого отдельного сканирования
            for scan_data in multiple_scan_data:
                individual_report = self._prepare_report_data(scan_data)
                batch_report_data['individual_reports'].append(individual_report)
            
            # Генерация batch отчетов
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_base_name = f"batch_report_{timestamp}"
            
            batch_report_paths = {}
            
            # JSON batch отчет
            json_batch_path = self.json_exporter.export_batch_report(
                batch_report_data, f"{batch_base_name}.json"
            )
            batch_report_paths['json'] = json_batch_path
            
            # CSV batch отчет
            csv_batch_path = self.csv_exporter.export_batch_report(
                batch_report_data, f"{batch_base_name}.csv"
            )
            batch_report_paths['csv'] = csv_batch_path
            
            self.logger.info(f"Batch reports generated: {list(batch_report_paths.keys())}")
            return batch_report_paths
            
        except Exception as e:
            self.logger.error(f"Error generating batch report: {str(e)}")
            return {'error': str(e)}
    
    def _generate_batch_summary(self, multiple_scan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация сводки по множественным сканированиям"""
        total_ads = 0
        total_urls = 0
        total_interactions = 0
        domains_covered = set()
        
        for scan_data in multiple_scan_data:
            total_ads += len(scan_data.get('detected_ads', []))
            total_urls += len(scan_data.get('processed_urls', []))
            total_interactions += len(scan_data.get('interaction_results', []))
            
            domain = scan_data.get('main_domain')
            if domain:
                domains_covered.add(domain)
        
        return {
            'total_scans': len(multiple_scan_data),
            'total_urls_processed': total_urls,
            'total_ads_detected': total_ads,
            'total_interactions': total_interactions,
            'domains_covered': list(domains_covered),
            'average_ads_per_url': total_ads / total_urls if total_urls > 0 else 0,
            'scan_period': {
                'start': min(
                    [s.get('scan_timestamp', datetime.now().isoformat()) 
                     for s in multiple_scan_data]
                ),
                'end': max(
                    [s.get('scan_timestamp', datetime.now().isoformat()) 
                     for s in multiple_scan_data]
                )
            }
        }