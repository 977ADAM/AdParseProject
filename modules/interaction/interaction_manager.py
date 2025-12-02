import logging
import time
from modules.interaction.click_emulator import ClickEmulator
from modules.interaction.redirect_tracker import RedirectTracker
from modules.interaction.url_analyzer import URLAnalyzer
from modules.screenshot.capturer import ScreenshotCapturer

class InteractionManager:
    """Главный класс для управления всем процессом взаимодействия с рекламой"""
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.click_emulator = ClickEmulator(driver, config)
        self.redirect_tracker = RedirectTracker(driver, config)
        self.url_analyzer = URLAnalyzer()
        self.screenshot_capturer = ScreenshotCapturer(driver, config)
    
    def perform_complete_ad_interaction(self, ad_data, max_interactions=2):
        """Выполнение полного цикла взаимодействия с рекламным блоком"""
        try:
            self.logger.info(f"Начинаем полный анализ взаимодействия для рекламы")
            
            element = ad_data.get('element')
            if not element:
                return {'error': 'No element provided'}
            
            results = {
                'ad_data': ad_data,
                'interactions': [],
                'summary': {},
                'screenshots': {}
            }
            
            clickability_analysis = self.click_emulator.analyze_clickability(element)
            results['clickability_analysis'] = clickability_analysis
            
            if not clickability_analysis.get('is_clickable', False):
                results['summary']['status'] = 'not_clickable'
                return results
            
            for i in range(min(max_interactions, 1 if not clickability_analysis['is_clickable'] else max_interactions)):
                interaction_result = self._perform_single_interaction_cycle(element, i+1)
                results['interactions'].append(interaction_result)
                
                # Пауза между взаимодействиями
                if i < max_interactions - 1:
                    time.sleep(2)
            
            results['summary'] = self._generate_interaction_summary(results)
            
            self.logger.info(f"Completed interaction analysis with {len(results['interactions'])} attempts")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in complete ad interaction: {str(e)}")
            return {
                'error': str(e),
                'ad_data': ad_data
            }
    
    def _perform_single_interaction_cycle(self, element, attempt_number):
        """Выполнение одного цикла взаимодействия"""
        try:
            cycle_result = {
                'attempt_number': attempt_number,
                'timestamp': time.time(),
                'screenshots': {}
            }
            
            original_window = self.driver.current_window_handle
            original_windows = set(self.driver.window_handles)
            original_url = self.driver.current_url
            
            before_screenshot = self.screenshot_capturer.capture_visible_area(
                f"before_interaction_{attempt_number}.png"
            )
            cycle_result['screenshots']['before'] = before_screenshot
            
            click_url = element.get_attribute('href') or original_url
            cycle_result['url_analysis_before'] = self.url_analyzer.analyze_ad_url(click_url)
            
            click_result = self.click_emulator.emulate_human_click(element)
            cycle_result['click_result'] = click_result
            
            if click_result.get('success', False):
                redirect_info = self.redirect_tracker.track_redirect(
                    attempt_number, original_window, original_windows, original_url, attempt_number
                )
                cycle_result['redirect_analysis'] = redirect_info
                
                # after_screenshot = self.screenshot_capturer.capture_visible_area(
                #     f"after_interaction_{attempt_number}.png"
                # )
                cycle_result['screenshots']['after'] = redirect_info.get('after_screenshot')
                
                if redirect_info.get('final_url'):
                    final_url_analysis = self.url_analyzer.analyze_ad_url(redirect_info['final_url'])
                    cycle_result['url_analysis_after'] = final_url_analysis
                    
                    if final_url_analysis.get('utm_analysis', {}).get('has_utm'):
                        cycle_result['utm_report'] = self.url_analyzer.generate_utm_report(
                            final_url_analysis['utm_analysis']
                        )
                
                self._restore_original_state(original_window, original_windows)
            
            return cycle_result
            
        except Exception as e:
            self.logger.error(f"Error in interaction cycle {attempt_number}: {str(e)}")
            return {
                'attempt_number': attempt_number,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _restore_original_state(self, original_window, original_windows):
        """Восстановление исходного состояния браузера"""
        try:
            current_windows = set(self.driver.window_handles)
            new_windows = current_windows - original_windows
            
            # Закрытие новых окон
            for window in new_windows:
                try:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                except:
                    pass
            
            # Возврат к исходному окну
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.logger.warning(f"Error restoring original state: {str(e)}")
    
    def _generate_interaction_summary(self, results):
        """Генерация сводки по всем взаимодействиям"""
        try:
            interactions = results.get('interactions', [])
            if not interactions:
                return {'total_attempts': 0, 'successful_attempts': 0}
            
            successful_interactions = [
                i for i in interactions 
                if i.get('click_result', {}).get('success', False)
            ]
            
            summary = {
                'total_attempts': len(interactions),
                'successful_attempts': len(successful_interactions),
                'success_rate': len(successful_interactions) / len(interactions) * 100,
                'redirect_types': [],
                'utm_found': False,
                'security_issues': []
            }
            
            for interaction in successful_interactions:
                redirect_analysis = interaction.get('redirect_analysis', {})
                url_analysis = interaction.get('url_analysis_after', {})
                
                redirect_type = redirect_analysis.get('redirect_type')
                if redirect_type and redirect_type not in summary['redirect_types']:
                    summary['redirect_types'].append(redirect_type)
                
                if url_analysis.get('utm_analysis', {}).get('has_utm'):
                    summary['utm_found'] = url_analysis.get('utm_analysis')
                
                security_analysis = url_analysis.get('security_analysis', {})
                if security_analysis.get('security_risk_score', 0) > 50:
                    summary['security_issues'].append({
                        'risk_score': security_analysis['security_risk_score'],
                        'url': url_analysis.get('url', 'Unknown')
                    })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating interaction summary: {str(e)}")
            return {'error': str(e)}