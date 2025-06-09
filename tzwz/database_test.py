#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoinBit数字期权交易平台 - 数据库连接测试脚本
用于测试数据库连接和基本操作
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """测试数据库连接"""
    print("🔍 开始测试数据库连接...")
    
    try:
        # 导入应用和数据库
        from app import create_app, db
        from app.models import User, Admin, SystemSettings
        
        app = create_app('development')
        
        with app.app_context():
            print("✅ Flask应用创建成功")
            
            # 测试数据库连接
            try:
                # 执行简单查询测试连接
                result = db.engine.execute('SELECT 1')
                print("✅ 数据库连接成功")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
            
            # 测试表是否存在
            try:
                admin_count = Admin.query.count()
                user_count = User.query.count()
                settings_count = SystemSettings.query.count()
                
                print(f"✅ 数据库表测试成功")
                print(f"   - 管理员数量: {admin_count}")
                print(f"   - 用户数量: {user_count}")
                print(f"   - 系统设置数量: {settings_count}")
                
                if admin_count == 0:
                    print("⚠️  警告: 未找到管理员账户，建议运行 python init_database.py")
                
            except Exception as e:
                print(f"❌ 数据库表不存在或查询失败: {e}")
                print("💡 建议运行: python init_database.py")
                return False
            
            print("🎉 数据库测试完成！")
            return True
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 建议安装依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_mysql_service():
    """检查MySQL服务状态"""
    print("\n🔍 检查MySQL服务状态...")
    
    import subprocess
    import platform
    
    try:
        if platform.system() == "Windows":
            # Windows系统检查MySQL服务
            result = subprocess.run(['sc', 'query', 'mysql'], 
                                  capture_output=True, text=True)
            if 'RUNNING' in result.stdout:
                print("✅ MySQL服务正在运行")
                return True
            else:
                print("❌ MySQL服务未运行")
                print("💡 请启动MySQL服务: net start mysql")
                return False
        else:
            # Linux/Mac系统检查
            result = subprocess.run(['systemctl', 'is-active', 'mysql'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ MySQL服务正在运行")
                return True
            else:
                print("❌ MySQL服务未运行")
                print("💡 请启动MySQL服务: sudo systemctl start mysql")
                return False
    except Exception as e:
        print(f"⚠️  无法检查MySQL服务状态: {e}")
        return None

def show_database_info():
    """显示数据库配置信息"""
    print("\n📊 数据库配置信息:")
    print("="*50)
    
    try:
        from config import DevelopmentConfig
        config = DevelopmentConfig()
        
        print(f"数据库URL: {config.SQLALCHEMY_DATABASE_URI}")
        print(f"支持的交易对: {config.TRADING_PAIRS}")
        print(f"最小充值金额: ${config.MIN_DEPOSIT}")
        print(f"最小提现金额: ${config.MIN_WITHDRAWAL}")
        print(f"WhatsApp客服: {config.WHATSAPP_NUMBER}")
        
    except Exception as e:
        print(f"无法加载配置信息: {e}")

def main():
    """主函数"""
    print("🚀 CoinBit数字期权交易平台 - 数据库测试")
    print("="*60)
    
    # 检查MySQL服务
    mysql_status = check_mysql_service()
    
    # 显示配置信息
    show_database_info()
    
    # 测试数据库连接
    if test_database_connection():
        print("\n🎯 测试结果: 数据库配置正常")
        print("\n💡 下一步操作:")
        print("1. 如果是首次运行，执行: python init_database.py")
        print("2. 启动应用: python app.py")
        print("3. 访问后台: http://localhost:5000/admin")
    else:
        print("\n❌ 测试结果: 数据库配置存在问题")
        print("\n🔧 故障排除:")
        print("1. 确保MySQL服务正在运行")
        print("2. 检查config.py中的数据库配置")
        print("3. 确保数据库用户有足够权限")
        print("4. 运行: pip install -r requirements.txt")
    
    print("="*60)

if __name__ == '__main__':
    main() 