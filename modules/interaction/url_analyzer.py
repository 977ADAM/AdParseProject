import logging
import re
from urllib.parse import urlparse, parse_qs, unquote

class URLAnalyzer:
    """Класс для детального анализа URL и UTM параметров"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.utm_patterns = self._initialize_utm_patterns()
    
    def _initialize_utm_patterns(self):
        """Инициализация паттернов UTM параметров"""
        return {
            'utm_source': {'description': 'Source of traffic', 'required': True},
            'utm_medium': {'description': 'Marketing medium', 'required': True},
            'utm_campaign': {'description': 'Campaign name', 'required': True},
            'utm_term': {'description': 'Keywords', 'required': False},
            'utm_content': {'description': 'Content variation', 'required': False},
            'utm_id': {'description': 'Campaign ID', 'required': False},
            'utm_source_platform': {'description': 'Source platform', 'required': False},
            'utm_creative_format': {'description': 'Creative format', 'required': False},
            'utm_marketing_tactic': {'description': 'Marketing tactic', 'required': False}
        }
    
    def analyze_ad_url(self, url, element_info=None):
        """Комплексный анализ рекламного URL"""
        try:
            analysis = {
                'url': url,
                'is_valid': self._validate_url(url),
                'parsed_components': self._parse_url_components(url),
                'utm_analysis': self._analyze_utm_parameters(url),
                'security_analysis': self._analyze_url_security(url),
                'redirect_analysis': self._analyze_redirect_patterns(url),
                'ad_network_indicators': self._find_ad_network_indicators(url),
                'element_context': element_info
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing URL: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'is_valid': False
            }
    
    def _validate_url(self, url):
        """Валидация URL"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
    
    def _parse_url_components(self, url):
        """Парсинг компонентов URL"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            return {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'domain': parsed.netloc,
                'tld': self._extract_tld(parsed.netloc),
                'query_parameters': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
                'query_parameter_count': len(query_params)
            }
        except Exception as e:
            self.logger.error(f"Error parsing URL components: {str(e)}")
            return {}
    
    def _extract_tld(self, netloc):
        """Извлечение TLD (Top-Level Domain)"""
        try:
            parts = netloc.split('.')
            if len(parts) >= 2:
                return '.'.join(parts[-2:])
            return netloc
        except:
            return netloc
    
    def _analyze_utm_parameters(self, url):
        """Анализ UTM параметров"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            utm_analysis = {
                'has_utm': False,
                'utm_parameters': {},
                'utm_completeness': 0,
                'missing_required': [],
                'found_optional': []
            }
            
            found_utms = {}
            required_found = 0
            total_required = 0
            
            for utm_key, utm_info in self.utm_patterns.items():
                if utm_info['required']:
                    total_required += 1
                
                if utm_key in query_params:
                    values = query_params[utm_key]
                    found_utms[utm_key] = {
                        'value': values[0] if values else '',
                        'description': utm_info['description'],
                        'required': utm_info['required']
                    }
                    
                    if utm_info['required']:
                        required_found += 1
                    else:
                        utm_analysis['found_optional'].append(utm_key)
            
            utm_analysis['utm_parameters'] = found_utms
            utm_analysis['has_utm'] = len(found_utms) > 0
            
            if total_required > 0:
                utm_analysis['utm_completeness'] = (required_found / total_required) * 100
            
            for utm_key, utm_info in self.utm_patterns.items():
                if utm_info['required'] and utm_key not in found_utms:
                    utm_analysis['missing_required'].append(utm_key)
            
            return utm_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing UTM parameters: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_url_security(self, url):
        """Анализ безопасности URL"""
        try:
            parsed = urlparse(url)
            
            security_indicators = {
                'is_https': parsed.scheme == 'https',
                'suspicious_tld': self._check_suspicious_tld(parsed.netloc),
                'ip_address': bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.netloc)),
                'suspicious_keywords': self._find_suspicious_keywords(url),
                'url_length': len(url),
                'has_encoded_chars': '%' in url,
                'multiple_subdomains': parsed.netloc.count('.') > 2
            }
            
            # Расчет общего score безопасности
            risk_score = 0
            if not security_indicators['is_https']:
                risk_score += 30
            if security_indicators['suspicious_tld']:
                risk_score += 25
            if security_indicators['ip_address']:
                risk_score += 20
            if security_indicators['suspicious_keywords']:
                risk_score += 15
            if security_indicators['has_encoded_chars']:
                risk_score += 10
            
            security_indicators['security_risk_score'] = min(risk_score, 100)
            security_indicators['security_level'] = (
                'high' if risk_score < 20 else 
                'medium' if risk_score < 50 else 
                'low'
            )
            
            return security_indicators
            
        except Exception as e:
            self.logger.error(f"Error analyzing URL security: {str(e)}")
            return {'error': str(e)}
    
    def _check_suspicious_tld(self, netloc):
        """Проверка на подозрительные TLD"""
        suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.loan', 
            '.win', '.review', '.club', '.work', '.site'
        ]
        
        return any(netloc.endswith(tld) for tld in suspicious_tlds)
    
    def _find_suspicious_keywords(self, url):
        """Поиск подозрительных ключевых слов в URL"""
        suspicious_keywords = [
            'login', 'password', 'bank', 'paypal', 'account',
            'verify', 'confirm', 'security', 'update', 'alert'
        ]
        
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in suspicious_keywords)
    
    def _analyze_redirect_patterns(self, url):
        """Анализ паттернов редиректа"""
        try:
            # Эвристический анализ для определения возможных редиректов
            redirect_indicators = {
                'has_redirect_params': any(param in url.lower() for param in ['redirect', 'return', 'next', 'goto']),
                'has_url_param': 'url=' in url.lower(),
                'has_http_in_param': re.search(r'=https?://', url) is not None,
                'encoded_url': re.search(r'%2F%2F|%3A%2F%2F', url) is not None
            }
            
            redirect_indicators['likely_redirect'] = (
                redirect_indicators['has_redirect_params'] or
                redirect_indicators['has_url_param'] or
                redirect_indicators['has_http_in_param'] or
                redirect_indicators['encoded_url']
            )
            
            return redirect_indicators
            
        except Exception as e:
            self.logger.error(f"Error analyzing redirect patterns: {str(e)}")
            return {'error': str(e)}
    
    def _find_ad_network_indicators(self, url):
        """Поиск индикаторов рекламных сетей в URL"""
        ad_network_patterns = {
            'google_ads': [r'doubleclick\.net', r'googleadservices\.com', r'googlesyndication\.com'],
            'facebook_ads': [r'facebook\.com/tr/', r'fbcdn\.net', r'atdmt\.com'],
            'yandex_ads': [r'yandex\.ru/ads', r'an\.yandex\.ru', r'yandexadexchange\.net'],
            'taboola': [r'taboola\.com'],
            'outbrain': [r'outbrain\.com'],
            'criteo': [r'criteo\.com']
        }
        
        detected_networks = []
        
        for network, patterns in ad_network_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    detected_networks.append(network)
                    break
        
        return {
            'detected_networks': detected_networks,
            'is_ad_network_url': len(detected_networks) > 0,
            'primary_network': detected_networks[0] if detected_networks else None
        }
    
    def generate_utm_report(self, utm_analysis):
        """Генерация отчета по UTM параметрам"""
        try:
            if not utm_analysis.get('has_utm', False):
                return {
                    'has_utm': False,
                    'message': 'No UTM parameters found'
                }
            
            report = {
                'has_utm': True,
                'completeness_score': utm_analysis.get('utm_completeness', 0),
                'completeness_level': 'high' if utm_analysis.get('utm_completeness', 0) > 80 else 'medium' if utm_analysis.get('utm_completeness', 0) > 50 else 'low',
                'parameters': {}
            }
            
            for utm_key, utm_data in utm_analysis.get('utm_parameters', {}).items():
                report['parameters'][utm_key] = {
                    'value': utm_data.get('value', ''),
                    'description': utm_data.get('description', ''),
                    'required': utm_data.get('required', False),
                    'decoded_value': unquote(utm_data.get('value', ''))
                }
            
            # Рекомендации
            recommendations = []
            if utm_analysis.get('utm_completeness', 0) < 100:
                recommendations.append(f"Missing required parameters: {', '.join(utm_analysis.get('missing_required', []))}")
            
            if len(utm_analysis.get('found_optional', [])) == 0:
                recommendations.append("Consider adding optional UTM parameters for better tracking")
            
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating UTM report: {str(e)}")
            return {'error': str(e)}