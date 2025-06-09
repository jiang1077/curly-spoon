import os
from datetime import timedelta

class Config:
    """CoinBit交易平台配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'coinbit-trading-platform-secret-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_db?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # 多语言配置
    LANGUAGES = {
        'zh': '中文',
        'en': 'English', 
        'ja': '日本語',
        'ko': '한국어',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'ru': 'Русский',
        'pt': 'Português',
        'it': 'Italiano',
        'nl': 'Nederlands',
        'tr': 'Türkçe',
        'ar': 'العربية',
        'hi': 'हिन्दी'
    }
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # 平台配置
    PLATFORM_NAME = 'CoinBit'
    PLATFORM_VERSION = '1.0.0'
    
    # 交易配置
    TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'XRP/USDT']
    OPTION_DURATIONS = {
        60: {'seconds': 60, 'profit_rate': 0.10, 'name': '60s'},
        90: {'seconds': 90, 'profit_rate': 0.15, 'name': '90s'}, 
        120: {'seconds': 120, 'profit_rate': 0.25, 'name': '120s'},
        180: {'seconds': 180, 'profit_rate': 0.35, 'name': '180s'},
        240: {'seconds': 240, 'profit_rate': 0.50, 'name': '240s'},
        300: {'seconds': 300, 'profit_rate': 0.80, 'name': '300s'}
    }
    
    # 资金配置
    MIN_DEPOSIT = 1.0  # 最小充值金额 1 USDT
    MIN_WITHDRAWAL = 5.0  # 最小提现金额 5 USDT
    WITHDRAWAL_FEE_RATE = 0.10  # 提现手续费 10%
    MIN_TRADE_AMOUNT = 1.0  # 最小交易金额
    MAX_TRADE_AMOUNT = 10000.0  # 最大交易金额
    
    # 支持的充值币种
    SUPPORTED_CURRENCIES = {
        'USDT-TRC20': {
            'name': 'USDT (TRC20)',
            'symbol': 'USDT',
            'network': 'TRC20',
            'recommended': True
        },
        'USDT-ERC20': {
            'name': 'USDT (ERC20)', 
            'symbol': 'USDT',
            'network': 'ERC20',
            'recommended': False
        }
    }
    
    # WhatsApp客服配置
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER') or '+1234567890'
    WHATSAPP_MESSAGE_TEMPLATE = """您好，我是CoinBit用户 {user_id}，需要咨询：
□ 充值问题
□ 提现问题
□ 交易问题
□ 账户问题
□ 其他问题"""

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_dev?charset=utf8mb4'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_test?charset=utf8mb4'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 