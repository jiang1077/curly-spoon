#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoinBit数字期权交易平台
主应用入口文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, db
from app.models import User, Admin, Order, Transaction, MarketPrice, SystemSettings

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Shell上下文处理器"""
    return {
        'db': db, 
        'User': User, 
        'Admin': Admin,
        'Order': Order,
        'Transaction': Transaction,
        'MarketPrice': MarketPrice,
        'SystemSettings': SystemSettings
    }

@app.cli.command()
def deploy():
    """部署命令"""
    from flask_migrate import upgrade
    from app.models import Admin, SystemSettings
    
    # 创建数据库表
    db.create_all()
    
    # 创建默认设置
    default_settings = {
        'site_name': 'CoinBit',
        'site_description': 'Professional Digital Options Trading Platform',
        'announcement': 'Welcome to CoinBit Trading Platform!',
        'whatsapp_number': '+1234567890',
        'maintenance_mode': 'false'
    }
    
    for key, value in default_settings.items():
        if not SystemSettings.query.get(key):
            setting = SystemSettings(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    print('Database deployed successfully!')

@app.cli.command()
def init_db():
    """初始化数据库命令"""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def create_admin():
    """创建管理员命令"""
    import click
    username = click.prompt('管理员用户名')
    email = click.prompt('管理员邮箱')
    password = click.prompt('管理员密码', hide_input=True)
    
    if Admin.query.filter_by(username=username).first():
        print(f'管理员用户名 {username} 已存在！')
        return
    
    admin = Admin(
        username=username,
        email=email,
        role='super_admin'
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f'超级管理员 {username} 创建成功！')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 