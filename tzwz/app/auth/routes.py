from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.auth import bp
from app.models import User, UserLoginLog, UserStatus
from app.forms import LoginForm, RegisterForm
from app import db
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(email=form.email.data).first()
        
        # 记录登录日志
        login_log = UserLoginLog(
            user_id=user.id if user else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            login_time=datetime.utcnow(),
            success=False
        )
        
        if user is None or not user.check_password(form.password.data):
            # 登录失败
            db.session.add(login_log)
            db.session.commit()
            flash('邮箱或密码错误', 'error')
            return render_template('auth/login.html', form=form)
        
        # 检查用户状态
        if user.status == UserStatus.DISABLED:
            db.session.add(login_log)
            db.session.commit()
            flash('账户已被禁用，请联系客服', 'error')
            return render_template('auth/login.html', form=form)
        
        # 登录成功
        login_log.success = True
        login_log.user_id = user.id
        user.last_login = datetime.utcnow()
        
        db.session.add(login_log)
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        flash(f'欢迎回来，{user.username}！', 'success')
        
        # 处理next参数
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='登录', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册 - 根据修改后的规划"""
    
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # 创建新用户 - 根据修改后的规划：状态为pending，需要上传证件审核
            user = User(
                username=form.username.data,
                email=form.email.data,
                status=UserStatus.PENDING,  # 待审核状态
                balance=0.00  # 初始余额为0
            )
            user.set_password(form.password.data)
            
            # 处理邀请码（如果有）
            if form.invite_code.data:
                # 这里可以添加邀请码逻辑
                # 根据修改后的规划，暂时移除了推荐奖励系统
                pass
            
            db.session.add(user)
            db.session.commit()
            
            # 记录登录日志
            login_log = UserLoginLog(
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                login_time=datetime.utcnow(),
                success=True
            )
            db.session.add(login_log)
            db.session.commit()
            
            # 自动登录
            login_user(user)
            
            flash('注册成功！请上传身份证件进行验证以激活账户。', 'success')
            return redirect(url_for('main.verify'))  # 跳转到证件上传页面
            
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'error')
    
    return render_template('auth/register.html', title='注册', form=form)

@bp.route('/logout')
def logout():
    """用户登出"""
    if current_user.is_authenticated:
        flash(f'再见，{current_user.username}！', 'info')
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/check_email')
def check_email():
    """检查邮箱是否已注册（AJAX接口）"""
    email = request.args.get('email')
    if not email:
        return {'exists': False}
    
    user = User.query.filter_by(email=email).first()
    return {'exists': user is not None}

@bp.route('/check_username')
def check_username():
    """检查用户名是否已注册（AJAX接口）"""
    username = request.args.get('username')
    if not username:
        return {'exists': False}
    
    user = User.query.filter_by(username=username).first()
    return {'exists': user is not None}

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 这里可以实现发送重置密码邮件的功能
    # 暂时只显示联系客服的提示
    
    return render_template('auth/forgot_password.html', title='忘记密码')

@bp.route('/terms')
def terms():
    """服务条款"""
    return render_template('auth/terms.html', title='服务条款')

@bp.route('/privacy')
def privacy():
    """隐私政策"""
    return render_template('auth/privacy.html', title='隐私政策')

# 语言切换
@bp.route('/set_language/<language>')
def set_language(language=None):
    """设置语言"""
    from flask import current_app
    
    if language in current_app.config['LANGUAGES']:
        session['language'] = language
        flash('语言设置已更新', 'success')
    
    # 返回到来源页面
    return redirect(request.referrer or url_for('main.index')) 