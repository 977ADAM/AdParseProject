from config.settings import Settings
from core.driver_manager import DriverManager
from modules.parser.page_loader import PageLoader
from modules.parser.html_analyzer import HTMLAnalyzer
from modules.detection.ad_detector import AdDetector
from modules.interaction.interaction_manager import InteractionManager
from modules.screenshot.capturer import ScreenshotCapturer
from modules.screenshot.annotator import ScreenshotAnnotator
from modules.screenshot.legend_builder import LegendBuilder
from modules.reporting.report_generator import ReportGenerator
from modules.interaction.simple_interaction_manager import SimpleInteractionManager
from modules.interaction.utm_analyzer import UTMAnalyzer
from utils.logger import setup_logging
import logging
import time
import json

def main():
    """Основная функция приложения"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    config = Settings()
    logger.info("Запуск приложения Ad Parser")
    
    urls = [
        "https://ria.ru/"
    ]

    driver_manager = DriverManager(config)

    all_scan_data = []
    
    try:
        for url in urls:
            logger.info(f"URL-адрес обработки: {url}")
            scan_start_time = time.time()

            with driver_manager as driver:

                if not driver:
                    logger.error("Не удалось создать драйвер")
                    continue

                page_loader = PageLoader(driver, config)

                ad_detector = AdDetector(driver, config)

                screenshot_capturer = ScreenshotCapturer(driver, config)

                # interaction_manager = InteractionManager(driver, config)
                interaction_manager = SimpleInteractionManager(driver, config)

                screenshot_annotator = ScreenshotAnnotator(config)
 
                legend_builder = LegendBuilder(config)

                if not page_loader.load_page(url):
                    logger.error(f"Не удалось загрузить страницу.: {url}")
                    continue

                page_loader.scroll_page()

                detected_ads = ad_detector.detect_ads()
                logger.info(f"Обнаружено {len(detected_ads)} реклам на {url}")

                # full_page_screenshot = screenshot_capturer.capture_full_page()
                # annotated_screenshot = None

                # if detected_ads and full_page_screenshot:
                #     annotated_screenshot = screenshot_annotator.annotate_ads_on_screenshot(
                #         full_page_screenshot, detected_ads
                #     )

                #     comparison_image = screenshot_annotator.create_comparison_image(
                #         full_page_screenshot,
                #         annotated_screenshot
                #     )

                #     legend_builder.create_detailed_legend_image(detected_ads)

                #     stats = legend_builder.create_summary_statistics(detected_ads)
                #     logger.info(f"Статистика обнаружения: {json.dumps(stats, indent=2)}")

                #     screenshot_capturer.capture_ads_screenshots(detected_ads)

                # interaction_results = []
                # for ad in detected_ads:
                #     interaction_result = interaction_manager.perform_complete_ad_interaction(ad, max_interactions=1)
                #     interaction_results.append(interaction_result)

                interaction_results = interaction_manager.test_multiple_ads(detected_ads, max_ads=2)

                scan_data = {
                    'url': url,
                    'main_domain': url.split('//')[-1].split('/')[0],
                    'scan_timestamp': time.time(),
                    'scan_duration': time.time() - scan_start_time,
                    'detected_ads': detected_ads,
                    'interaction_results': interaction_results,

                    'processed_urls': [url]
                }

                all_scan_data.append(scan_data)

                logger.info(f"Завершена обработка для {url}")
        
        if all_scan_data:
            logger.info("Создание комплексных отчетов...")
            report_generator = ReportGenerator(config)

            individual_reports = []
            for scan_data in all_scan_data:
                report_paths = report_generator.generate_comprehensive_report(scan_data)
                individual_reports.append({
                    'domain': scan_data.get('main_domain'),
                    'report_paths': report_paths
                })
                logger.info(f"Generated reports for {scan_data.get('main_domain')}: {report_paths}")

            batch_report_paths = report_generator.generate_batch_report(all_scan_data)

            final_summary = {
                'total_domains_processed': len(all_scan_data),
                'total_ads_detected': sum(len(scan.get('detected_ads', [])) for scan in all_scan_data),
                'total_interactions': sum(len(scan.get('interaction_results', [])) for scan in all_scan_data),
                'individual_reports': individual_reports,
                'batch_report': batch_report_paths,
                'generated_at': time.time()
            }

            summary_path = config.OUTPUT_DIR / "final_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(final_summary, f, indent=2, ensure_ascii=False)
        
        else:
            logger.warning("No scan data collected - skipping report generation")

    except Exception as e:
        logger.error(f"Ошибка приложения: {str(e)}")
    
    finally:
        logger.info("Приложение Ad Parser завершено")

if __name__ == "__main__":
    main()