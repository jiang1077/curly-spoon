#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoinBit数字期权交易平台 - 数据库初始化脚本
运行此脚本可以创建数据库表结构并插入示例数据
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import (
        User, Admin, Order, Transaction, MarketPrice, SystemSettings, UserLoginLog,
        UserStatus, OrderDirection, OrderResult, TransactionType, TransactionStatus, ProfitControl
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需依赖: flask, flask-sqlalchemy, pymysql")
    sys.exit(1)

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("🔧 开始初始化数据库...")
        
        # 删除所有表（如果存在）
        print("🗑️  删除现有表...")
        db.drop_all()
        
        # 创建所有表
        print("🏗️  创建数据库表...")
        db.create_all()
        
        # 插入系统设置
        print("⚙️  插入系统设置...")
        create_system_settings()
        
        # 创建默认管理员
        print("👑 创建默认管理员...")
        create_default_admin()
        
        # 创建示例用户
        print("👥 创建示例用户...")
        create_sample_users()
        
        # 插入市场价格数据
        print("📈 插入市场价格数据...")
        create_market_prices()
        
        # 创建示例订单
        print("📋 创建示例订单...")
        create_sample_orders()
        
        # 创建示例交易记录
        print("💰 创建示例交易记录...")
        create_sample_transactions()
        
        # 提交所有更改
        db.session.commit()
        print("✅ 数据库初始化完成！")
        
        # 显示初始化信息
        show_init_info()

def create_system_settings():
    """创建系统设置"""
    settings = [
        ('site_name', 'CoinBit', '网站名称'),
        ('site_description', 'Professional Digital Options Trading Platform', '网站描述'),
        ('announcement', '欢迎来到CoinBit数字期权交易平台！', '系统公告'),
        ('whatsapp_number', '+1234567890', 'WhatsApp客服号码'),
        ('maintenance_mode', 'false', '维护模式'),
        ('min_deposit', '1.00', '最小充值金额'),
        ('min_withdrawal', '5.00', '最小提现金额'),
        ('withdrawal_fee_rate', '0.10', '提现手续费率'),
        ('usdt_trc20_address', 'TQrZ9wBk8A1ABCD1234567890EFGHIJklmno', 'USDT TRC20充值地址'),
        ('usdt_trc20_backup', 'TPqX8vCj9B2XYZA9876543210QRSTUVwxyz', 'USDT TRC20备用地址'),
    ]
    
    for key, value, description in settings:
        setting = SystemSettings(key=key, value=value, description=description)
        db.session.add(setting)

def create_default_admin():
    """创建默认管理员"""
    # 超级管理员
    super_admin = Admin(
        username='admin',
        email='admin@coinbit.com',
        role='super_admin'
    )
    super_admin.set_password('admin123')
    db.session.add(super_admin)
    
    # 普通管理员
    admin = Admin(
        username='manager',
        email='manager@coinbit.com',
        role='admin'
    )
    admin.set_password('manager123')
    db.session.add(admin)

def create_sample_users():
    """创建示例用户"""
    users_data = [
        {
            'username': 'user001',
            'email': 'user001@example.com',
            'password': 'password123',
            'balance': Decimal('1250.50'),
            'status': UserStatus.ACTIVE,
            'real_name': '张三',
            'id_number': '310101199001011234'
        },
        {
            'username': 'trader123',
            'email': 'trader123@example.com',
            'password': 'password123',
            'balance': Decimal('3780.25'),
            'status': UserStatus.ACTIVE,
            'real_name': '李四',
            'id_number': '310101199002021234'
        },
        {
            'username': 'investor_pro',
            'email': 'investor@example.com',
            'password': 'password123',
            'balance': Decimal('0.00'),
            'status': UserStatus.PENDING,
            'real_name': '王五',
            'id_number': '310101199003031234'
        },
        {
            'username': 'crypto_fan',
            'email': 'crypto@example.com',
            'password': 'password123',
            'balance': Decimal('520.80'),
            'status': UserStatus.ACTIVE,
            'real_name': '赵六',
            'id_number': '310101199004041234'
        },
        {
            'username': 'newbie2024',
            'email': 'newbie@example.com',
            'password': 'password123',
            'balance': Decimal('0.00'),
            'status': UserStatus.PENDING,
            'real_name': '钱七',
            'id_number': '310101199005051234'
        }
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            balance=user_data['balance'],
            status=user_data['status'],
            real_name=user_data['real_name'],
            id_number=user_data['id_number'],
            created_at=datetime.utcnow() - timedelta(days=30, hours=12)
        )
        user.set_password(user_data['password'])
        user.set_fund_password('123456')  # 统一资金密码
        db.session.add(user)

def create_market_prices():
    """创建市场价格数据"""
    symbols_data = [
        ('BTC/USDT', Decimal('43500.00'), Decimal('2.5'), Decimal('1250000000')),
        ('ETH/USDT', Decimal('2420.50'), Decimal('-1.2'), Decimal('850000000')),
        ('LTC/USDT', Decimal('75.25'), Decimal('3.8'), Decimal('120000000')),
        ('XRP/USDT', Decimal('0.485'), Decimal('-0.5'), Decimal('95000000')),
        ('BNB/USDT', Decimal('315.20'), Decimal('1.8'), Decimal('45000000')),
        ('ADA/USDT', Decimal('0.485'), Decimal('0.2'), Decimal('65000000'))
    ]
    
    for symbol, price, change_24h, volume_24h in symbols_data:
        market_price = MarketPrice(
            symbol=symbol,
            price=price,
            change_24h=change_24h,
            volume_24h=volume_24h,
            timestamp=datetime.utcnow()
        )
        db.session.add(market_price)

def create_sample_orders():
    """创建示例订单"""
    orders_data = [
        {
            'user_id': 1, 'symbol': 'BTC/USDT', 'direction': OrderDirection.UP,
            'amount': Decimal('100.00'), 'duration': 60, 'profit_rate': Decimal('0.80'),
            'start_price': Decimal('43500.00'), 'end_price': Decimal('43520.00'),
            'result': OrderResult.WIN, 'created_at': datetime.utcnow() - timedelta(hours=2)
        },
        {
            'user_id': 2, 'symbol': 'ETH/USDT', 'direction': OrderDirection.DOWN,
            'amount': Decimal('50.00'), 'duration': 120, 'profit_rate': Decimal('0.85'),
            'start_price': Decimal('2420.50'), 'end_price': Decimal('2415.30'),
            'result': OrderResult.WIN, 'created_at': datetime.utcnow() - timedelta(hours=1)
        },
        {
            'user_id': 1, 'symbol': 'BTC/USDT', 'direction': OrderDirection.UP,
            'amount': Decimal('200.00'), 'duration': 300, 'profit_rate': Decimal('0.90'),
            'start_price': Decimal('43480.00'), 'result': OrderResult.PENDING,
            'created_at': datetime.utcnow() - timedelta(minutes=3)
        }
    ]
    
    for order_data in orders_data:
        order = Order(**order_data)
        if order.result == OrderResult.WIN:
            order.profit_amount = order.amount * order.profit_rate
            order.settled_at = order.created_at + timedelta(seconds=order.duration)
        db.session.add(order)

def create_sample_transactions():
    """创建示例交易记录"""
    transactions_data = [
        {
            'user_id': 1, 'type': TransactionType.DEPOSIT, 'amount': Decimal('1000.00'),
            'status': TransactionStatus.COMPLETED, 'description': 'USDT TRC20充值',
            'wallet_address': 'TQrZ9wBk8A1ABCD1234567890EFGHIJklmno',
            'network': 'TRC20', 'tx_hash': 'abc123def456',
            'created_at': datetime.utcnow() - timedelta(days=1)
        },
        {
            'user_id': 2, 'type': TransactionType.DEPOSIT, 'amount': Decimal('5000.00'),
            'status': TransactionStatus.COMPLETED, 'description': 'USDT TRC20充值',
            'wallet_address': 'TQrZ9wBk8A1ABCD1234567890EFGHIJklmno',
            'network': 'TRC20', 'tx_hash': 'def456ghi789',
            'created_at': datetime.utcnow() - timedelta(days=2)
        },
        {
            'user_id': 1, 'type': TransactionType.WITHDRAWAL, 'amount': Decimal('500.00'),
            'status': TransactionStatus.PENDING, 'description': 'USDT TRC20提现',
            'wallet_address': 'TUserWalletAddress123456789',
            'network': 'TRC20', 'fee_amount': Decimal('50.00'),
            'created_at': datetime.utcnow() - timedelta(hours=6)
        }
    ]
    
    for trans_data in transactions_data:
        transaction = Transaction(**trans_data)
        if transaction.status == TransactionStatus.COMPLETED:
            transaction.completed_at = transaction.created_at + timedelta(minutes=10)
        db.session.add(transaction)

def show_init_info():
    """显示初始化信息"""
    print("\n" + "="*60)
    print("🎉 CoinBit数据库初始化完成！")
    print("="*60)
    print("\n📊 初始化数据统计:")
    print(f"👑 管理员账户: {Admin.query.count()} 个")
    print(f"👥 用户账户: {User.query.count()} 个")
    print(f"📋 交易订单: {Order.query.count()} 个")
    print(f"💰 交易记录: {Transaction.query.count()} 个")
    print(f"📈 市场价格: {MarketPrice.query.count()} 个")
    print(f"⚙️  系统设置: {SystemSettings.query.count()} 个")
    
    print("\n🔑 默认账户信息:")
    print("超级管理员 - 用户名: admin, 密码: admin123")
    print("普通管理员 - 用户名: manager, 密码: manager123")
    print("测试用户 - 用户名: user001, 密码: password123")
    
    print("\n🌐 访问地址:")
    print("前台: http://localhost:5000")
    print("后台: http://localhost:5000/admin")
    
    print("\n💡 下一步操作:")
    print("1. 运行: python app.py")
    print("2. 访问后台管理系统")
    print("3. 使用admin/admin123登录")
    print("="*60)

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1) 