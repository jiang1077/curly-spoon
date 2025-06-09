from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, MarketPrice, SystemSettings, Order, Transaction
from app.forms import ProfileForm, IDCardUploadForm
from app import db
from datetime import datetime, timedelta
import os
import secrets
from werkzeug.utils import secure_filename

@bp.route('/')
@bp.route('/index')
def index():
    """首页路由 - 根据修改后的规划显示价格和公告"""
    
    # 获取系统公告
    announcement = SystemSettings.get_setting('announcement', 'Welcome to CoinBit Trading Platform!')
    
    # 获取主流加密货币和黄金的实时价格（根据修改后的规划）
    crypto_prices = []
    symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'XRP/USDT', 'GOLD/USDT']
    
    for symbol in symbols:
        latest_price = MarketPrice.get_latest_price(symbol)
        if latest_price:
            crypto_prices.append({
                'symbol': symbol,
                'price': float(latest_price.price),
                'change_24h': float(latest_price.change_24h) if latest_price.change_24h else 0,
                'volume_24h': float(latest_price.volume_24h) if latest_price.volume_24h else 0
            })
        else:
            # 如果没有价格数据，生成模拟数据用于演示
            import random
            base_prices = {
                'BTC/USDT': 96130.23,
                'ETH/USDT': 3420.15,
                'LTC/USDT': 85.67,
                'XRP/USDT': 0.5234,
                'GOLD/USDT': 2035.50
            }
            crypto_prices.append({
                'symbol': symbol,
                'price': base_prices.get(symbol, 100.0) + random.uniform(-5, 5),
                'change_24h': random.uniform(-5, 5),
                'volume_24h': random.uniform(100000, 1000000)
            })
    
    # 统计数据（如果用户已登录）
    user_stats = None
    if current_user.is_authenticated:
        user_stats = {
            'total_orders': current_user.orders.count(),
            'win_orders': current_user.orders.filter_by(result='win').count(),
            'total_profit': sum([float(order.profit_amount) for order in current_user.orders.filter_by(result='win')]),
            'available_balance': current_user.get_available_balance()
        }
    
    return render_template('main/index.html',
                         title='首页',
                         announcement=announcement,
                         crypto_prices=crypto_prices,
                         user_stats=user_stats)

@bp.route('/profile')
@login_required
def profile():
    """个人中心"""
    
    # 获取用户统计数据
    total_orders = current_user.orders.count()
    win_orders = current_user.orders.filter_by(result='win').count()
    lose_orders = current_user.orders.filter_by(result='lose').count()
    win_rate = (win_orders / total_orders * 100) if total_orders > 0 else 0
    
    # 最近订单
    recent_orders = current_user.orders.order_by(Order.created_at.desc()).limit(10).all()
    
    # 最近交易记录
    recent_transactions = current_user.transactions.order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template('main/profile.html',
                         title='个人中心',
                         total_orders=total_orders,
                         win_orders=win_orders,
                         lose_orders=lose_orders,
                         win_rate=win_rate,
                         recent_orders=recent_orders,
                         recent_transactions=recent_transactions)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """账户设置"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            # 更新用户名
            if form.username.data != current_user.username:
                # 检查用户名是否已存在
                existing_user = User.query.filter_by(username=form.username.data).first()
                if existing_user and existing_user.id != current_user.id:
                    flash('该用户名已被使用', 'error')
                    return render_template('main/settings.html', form=form)
                current_user.username = form.username.data
            
            # 更新密码
            if form.new_password.data:
                if not form.current_password.data:
                    flash('请输入当前密码', 'error')
                    return render_template('main/settings.html', form=form)
                
                if not current_user.check_password(form.current_password.data):
                    flash('当前密码错误', 'error')
                    return render_template('main/settings.html', form=form)
                
                current_user.set_password(form.new_password.data)
                flash('密码修改成功', 'success')
            
            # 设置资金密码
            if form.fund_password.data:
                current_user.set_fund_password(form.fund_password.data)
                flash('资金密码设置成功', 'success')
            
            db.session.commit()
            flash('设置保存成功', 'success')
            return redirect(url_for('main.settings'))
            
        except Exception as e:
            db.session.rollback()
            flash('保存失败，请重试', 'error')
    
    # 预填充表单
    form.username.data = current_user.username
    
    return render_template('main/settings.html', form=form)

@bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    """身份验证 - 证件上传"""
    
    # 检查是否已经提交过证件
    if current_user.id_card_front and current_user.id_card_back:
        flash('您已提交过身份证件，请等待审核', 'info')
        return redirect(url_for('main.profile'))
    
    form = IDCardUploadForm()
    
    if form.validate_on_submit():
        try:
            # 创建上传目录
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'id_cards')
            os.makedirs(upload_folder, exist_ok=True)
            
            # 保存证件正面
            if form.id_card_front.data:
                front_filename = secure_filename(f"{current_user.id}_{secrets.token_hex(8)}_front.{form.id_card_front.data.filename.rsplit('.', 1)[1].lower()}")
                front_path = os.path.join(upload_folder, front_filename)
                form.id_card_front.data.save(front_path)
                current_user.id_card_front = f"uploads/id_cards/{front_filename}"
            
            # 保存证件反面
            if form.id_card_back.data:
                back_filename = secure_filename(f"{current_user.id}_{secrets.token_hex(8)}_back.{form.id_card_back.data.filename.rsplit('.', 1)[1].lower()}")
                back_path = os.path.join(upload_folder, back_filename)
                form.id_card_back.data.save(back_path)
                current_user.id_card_back = f"uploads/id_cards/{back_filename}"
            
            # 保存证件信息
            current_user.real_name = form.real_name.data
            current_user.id_number = form.id_number.data
            
            db.session.commit()
            flash('证件上传成功，请等待管理员审核', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('上传失败，请重试', 'error')
    
    return render_template('main/verify.html', form=form)

@bp.route('/api/prices')
def api_prices():
    """API接口：获取实时价格数据"""
    
    prices = []
    symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'XRP/USDT', 'GOLD/USDT']
    
    for symbol in symbols:
        latest_price = MarketPrice.get_latest_price(symbol)
        if latest_price:
            prices.append({
                'symbol': symbol,
                'price': float(latest_price.price),
                'change_24h': float(latest_price.change_24h) if latest_price.change_24h else 0,
                'timestamp': latest_price.timestamp.isoformat()
            })
        else:
            # 生成模拟价格数据
            import random
            base_prices = {
                'BTC/USDT': 96130.23,
                'ETH/USDT': 3420.15,
                'LTC/USDT': 85.67,
                'XRP/USDT': 0.5234,
                'GOLD/USDT': 2035.50
            }
            prices.append({
                'symbol': symbol,
                'price': base_prices.get(symbol, 100.0) + random.uniform(-10, 10),
                'change_24h': random.uniform(-5, 5),
                'timestamp': datetime.utcnow().isoformat()
            })
    
    return jsonify(prices)

@bp.route('/about')
def about():
    """关于我们"""
    return render_template('main/about.html', title='关于我们')

@bp.route('/contact')
def contact():
    """联系我们"""
    whatsapp_number = SystemSettings.get_setting('whatsapp_number', '+1234567890')
    return render_template('main/contact.html', 
                         title='联系我们',
                         whatsapp_number=whatsapp_number)

@bp.route('/help')
def help():
    """帮助中心"""
    return render_template('main/help.html', title='帮助中心')

# 生成测试价格数据的辅助函数
@bp.route('/admin/generate_test_prices')
@login_required
def generate_test_prices():
    """生成测试价格数据（仅用于开发测试）"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:
        import random
        symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'XRP/USDT', 'GOLD/USDT']
        base_prices = {
            'BTC/USDT': 96130.23,
            'ETH/USDT': 3420.15,
            'LTC/USDT': 85.67,
            'XRP/USDT': 0.5234,
            'GOLD/USDT': 2035.50
        }
        
        for symbol in symbols:
            # 生成最近1小时的价格数据
            for i in range(60):
                timestamp = datetime.utcnow() - timedelta(minutes=i)
                price = base_prices[symbol] + random.uniform(-20, 20)
                change_24h = random.uniform(-5, 5)
                volume_24h = random.uniform(100000, 1000000)
                
                market_price = MarketPrice(
                    symbol=symbol,
                    price=price,
                    change_24h=change_24h,
                    volume_24h=volume_24h,
                    timestamp=timestamp
                )
                db.session.add(market_price)
        
        db.session.commit()
        flash('测试价格数据生成成功', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('生成测试数据失败', 'error')
    
    return redirect(url_for('main.index')) 