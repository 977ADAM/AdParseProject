class AdPatterns:
    """Паттерны для обнаружения рекламных элементов"""
    # Рекламные сети и домены
    AD_NETWORKS = {
        # 'google_ads': [
        #     'doubleclick.net',
        #     'googleadservices.com',
        #     'googlesyndication.com',
        #     'google-analytics.com',
        #     'gstatic.com',
        #     'adsense',
        #     'pagead',
        #     'adservice'
        # ],
        'yandex_ads': [
            # 'yandex.ru/ads',
            # 'yandexadexchange.net',
            # 'an.yandex.ru',
            'yandex.ru/adfox',
            'yandex.ru/an',
            # 'yandex.ru/direct'
        ],
        # 'meta_ads': [
        #     'facebook.com/ads',
        #     'fbcdn.net',
        #     'facebook.com/tr/',
        #     'atdmt.com',
        #     'adsystem'
        # ],
        # 'tiktok_ads': [
        #     'tiktok.com/ads',
        #     'bytedance.com',
        #     'byteoversea.com'
        # ],
        # 'amazon_ads': [
        #     'amazon-adsystem.com',
        #     'assoc-amazon.com'
        # ],
        # 'other_networks': [
        #     'adsystem',
        #     'adserver',
        #     'advertising',
        #     'ads.',
        #     'adfox',
        #     'adriver',
        #     'myarget',
        #     'openx.net',
        #     'criteo.com',
        #     'taboola.com',
        #     'outbrain.com',
        #     'adsnative',
        #     'revcontent'
        # ]
    }
    
    # HTML классы и атрибуты рекламы
    AD_CLASS_PATTERNS = [
        'yandex_rtb_',
        'adfox_',
        # 'ad',
        # 'ads',
        # 'advertisement',
        # 'advertising',
        # 'banner',
        # 'banner__content',
        # 'section__banner-slide',
        # 'section__banner-column',
        # 'section__banner-after',
        # 'b-header-adv-stripe__banner-wrapper',
        # 'b-header-adv-stripe__banner',
        # 'ad-container',
        # 'ad-wrapper',
        # 'ad-area',
        # 'ad-space',
        # 'ad-unit',
        # 'ad-block',
        # 'ad-placeholder',
        # 'ad-slot',
        # 'adbox', 
        # 'adframe',
        # 'advert',
        # 'adv',
        # 'publicite',
        # 'sponsor',
        # 'promo',
        # 'commercial',
        # 'affiliate',
        # 'doubleclick',
        # 'google_ad',
        # 'adsbygoogle',
        # 'yandex-ad',
        # 'yandex-direct',
        # 'fb-ad',
        # 'ad-',
        # '-ad',
        # '_ad',
        # 'ad_'
    ]
    
    # Data атрибуты рекламы
    AD_DATA_ATTRIBUTES = [
        'data-ad', 'data-ad-client', 'data-ad-slot', 'data-ad-unit',
        'data-ad-width', 'data-ad-height', 'data-ad-format',
        'data-ad-layout', 'data-ad-region', 'data-ad-provider',
        'data-ad-network', 'data-ad-type', 'data-ad-status',
        'data-ad-request', 'data-ad-response', 'data-ad-targeting'
    ]
    
    # ID паттерны рекламы
    AD_ID_PATTERNS = [
        'yandex_rtb_',
        'adfox_',
        'begun_block_',
        # 'banner_before_header_index',
        # 'ad',
        # 'ads',
        # 'banner',
        # 'advert',
        # 'adv',
        # 'sponsor',
        # 'promo',
        # 'ad-container',
        # 'ad-wrapper',
        # 'ad-unit',
        # 'ad-frame',
        # 'ad-space',
        # 'ad-block',
        # 'ad-slot'
    ]
    
    # Стандартные размеры рекламных баннеров (width x height)
    STANDARD_AD_SIZES = [
        (300, 250),   # Medium Rectangle
        (336, 280),   # Large Rectangle
        (728, 90),    # Leaderboard
        (970, 90),    # Super Leaderboard
        (970, 250),   # Billboard
        (300, 600),   # Half Page
        (160, 600),   # Wide Skyscraper
        (120, 600),   # Skyscraper
        (320, 100),   # Large Mobile Banner
        (320, 50),    # Mobile Banner
        (468, 60),    # Banner
        (234, 60),    # Half Banner
        (120, 240),   # Vertical Banner
        (250, 250),   # Square
        (200, 200),   # Small Square
        (180, 150),   # Small Rectangle
        (125, 125),   # Button
        (240, 400),   # Vertical Rectangle
        (300, 1050),  # Portrait
        (970, 90),    # Large Leaderboard
        (970, 66),    # Super Leaderboard
        (88, 31)      # Micro Bar
    ]
    
    # Рекламные ключевые слова в тексте и атрибутах
    AD_KEYWORDS = [
        'ad',
        'ads',
        'adv',
        # 'advert',
        # 'advertisement',
        'banner',
        # 'sponsor',
        # 'sponsored',
        # 'promoted',
        # 'promotion',
        # 'commercial',
        # 'affiliate',
        # 'partner',
        # 'doubleclick',
        # 'googlead',
        # 'adsense',
        # 'yandex',
        # 'direct',
        # 'adfox',
        # 'facebook',
        # 'instagram',
        # 'tiktok',
        # 'click',
        # 'impression',
        # 'ctr',
        # 'cpm',
        # 'cpc',
        # 'campaign',
        # 'targeting',
        # 'retargeting'
    ]
    
    # Скрипты рекламных сетей
    AD_SCRIPT_PATTERNS = [
        'googletag', 'google_ad', 'adsbygoogle',
        'yaContext', 'yandexContext', 'adfox',
        'fbq', 'facebook-pixel', 'tr(',
        'ttq', 'tiktok-pixel',
        'amazon-adsystem', 'aax.com',
        'taboola', 'outbrain', 'revcontent',
        'criteo', 'pubmatic', 'rubicon'
    ]