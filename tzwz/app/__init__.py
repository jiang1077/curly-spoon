from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_mail import Mail
from config import config
import os

# 扩展初始化
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()
mail = Mail()

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)
    mail.init_app(app)
    
    # 登录管理器配置
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # 多语言支持
    @babel.localeselector
    def get_locale():
        # 1. 检查URL参数
        if request.args.get('lang'):
            session['language'] = request.args.get('lang')
        # 2. 检查session
        if 'language' in session and session['language'] in app.config['LANGUAGES']:
            return session['language']
        # 3. 检查浏览器偏好
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'zh'
    
    # 注册蓝图
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.trading import bp as trading_bp
    app.register_blueprint(trading_bp, url_prefix='/trading')
    
    from app.wallet import bp as wallet_bp
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 全局模板变量
    @app.context_processor
    def inject_conf_vars():
        from flask_babel import get_locale
        return {
            'PLATFORM_NAME': app.config['PLATFORM_NAME'],
            'LANGUAGES': app.config['LANGUAGES'],
            'CURRENT_LANGUAGE': str(get_locale()),
            'WHATSAPP_NUMBER': app.config['WHATSAPP_NUMBER']
        }
    
    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账户
        from app.models import Admin
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                email='admin@coinbit.com',
                role='super_admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin account: admin/admin123")
    
    return app 