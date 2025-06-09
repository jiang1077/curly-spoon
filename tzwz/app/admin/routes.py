#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员路由模块
处理所有管理员相关的路由和功能
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import Admin, User, Order, Transaction, SystemSettings
from ..forms import AdminLoginForm
from datetime import datetime, timedelta
import os

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录"""
    if current_user.is_authenticated and hasattr(current_user, 'role'):
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin_user = Admin.query.filter_by(username=form.username.data).first()
        
        if admin_user and admin_user.verify_password(form.password.data):
            if admin_user.status.value != 'active':
                flash('管理员账号已被禁用，请联系超级管理员', 'error')
                return render_template('admin/login.html', form=form)
            
            login_user(admin_user, remember=form.remember_me.data)
            
            # 记录登录日志
            admin_user.last_login = datetime.utcnow()
            admin_user.login_count = (admin_user.login_count or 0) + 1
            db.session.commit()
            
            flash(f'欢迎回来，{admin_user.username}！', 'success')
            
            # 重定向到原来想访问的页面或仪表板
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@login_required
def logout():
    """管理员登出"""
    logout_user()
    flash('您已安全退出管理系统', 'success')
    return redirect(url_for('admin.login'))

@admin.route('/dashboard')
@login_required
def dashboard():
    """管理仪表板"""
    if not hasattr(current_user, 'role'):
        flash('权限不足，请使用管理员账号登录', 'error')
        return redirect(url_for('admin.login'))
    
    # 统计数据
    total_users = User.query.count()
    pending_users = User.query.filter_by(status='pending').count()
    active_users = User.query.filter_by(status='active').count()
    
    # 今日订单数
    today = datetime.utcnow().date()
    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()
    
    # 待审核用户列表（最近5个）
    pending_verifications = User.query.filter_by(status='pending')\
        .order_by(User.created_at.desc()).limit(5).all()
    
    # 最近注册用户（最近5个）
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         pending_users=pending_users,
                         active_users=active_users,
                         today_orders=today_orders,
                         pending_verifications=pending_verifications,
                         recent_users=recent_users)

@admin.route('/users')
@login_required
def users():
    """用户管理页面"""
    if not hasattr(current_user, 'role'):
        flash('权限不足', 'error')
        return redirect(url_for('admin.login'))
    
    # 获取筛选参数
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    query = User.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.phone.contains(search)
            )
        )
    
    # 分页
    users_pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html',
                         users=users_pagination.items,
                         pagination=users_pagination,
                         current_status=status,
                         search_query=search)

@admin.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    """用户详情页面"""
    if not hasattr(current_user, 'role'):
        flash('权限不足', 'error')
        return redirect(url_for('admin.login'))
    
    user = User.query.get_or_404(user_id)
    
    # 获取用户的订单历史
    orders = Order.query.filter_by(user_id=user_id)\
        .order_by(Order.created_at.desc()).limit(10).all()
    
    # 获取用户的交易记录
    transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         orders=orders,
                         transactions=transactions)

@admin.route('/verify_user/<int:user_id>/<action>')
@login_required
def verify_user(user_id, action):
    """用户审核操作"""
    if not hasattr(current_user, 'role'):
        flash('权限不足', 'error')
        return redirect(url_for('admin.login'))
    
    user = User.query.get_or_404(user_id)
    
    if action == 'approve':
        user.status = 'active'
        user.verified_at = datetime.utcnow()
        user.verified_by = current_user.id
        flash(f'用户 {user.username} 审核通过', 'success')
        
    elif action == 'reject':
        user.status = 'rejected'
        user.verified_at = datetime.utcnow()
        user.verified_by = current_user.id
        flash(f'用户 {user.username} 审核拒绝', 'warning')
        
    elif action == 'disable':
        user.status = 'disabled'
        flash(f'用户 {user.username} 已禁用', 'warning')
        
    elif action == 'enable':
        user.status = 'active'
        flash(f'用户 {user.username} 已启用', 'success')
    
    db.session.commit()
    
    # 重定向回原页面
    return redirect(request.referrer or url_for('admin.users'))

@admin.route('/system_settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    """系统设置页面"""
    if not hasattr(current_user, 'role') or current_user.role.value != 'super_admin':
        flash('权限不足，需要超级管理员权限', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        # 更新系统设置
        settings_data = request.get_json() if request.is_json else request.form
        
        for key, value in settings_data.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting = SystemSettings.query.get(setting_key)
                
                if setting:
                    setting.value = value
                else:
                    setting = SystemSettings(key=setting_key, value=value)
                    db.session.add(setting)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': '设置已更新'})
        else:
            flash('系统设置已更新', 'success')
            return redirect(url_for('admin.system_settings'))
    
    # 获取所有系统设置
    settings = {}
    for setting in SystemSettings.query.all():
        settings[setting.key] = setting.value
    
    return render_template('admin/system_settings.html', settings=settings)

@admin.route('/orders')
@login_required
def orders():
    """订单管理页面"""
    if not hasattr(current_user, 'role'):
        flash('权限不足', 'error')
        return redirect(url_for('admin.login'))
    
    # 获取筛选参数
    status = request.args.get('status', 'all')
    symbol = request.args.get('symbol', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    query = Order.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if symbol != 'all':
        query = query.filter_by(symbol=symbol)
    
    # 分页
    orders_pagination = query.order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取所有交易对
    symbols = db.session.query(Order.symbol).distinct().all()
    symbols = [s[0] for s in symbols]
    
    return render_template('admin/orders.html',
                         orders=orders_pagination.items,
                         pagination=orders_pagination,
                         current_status=status,
                         current_symbol=symbol,
                         symbols=symbols)

@admin.route('/transactions')
@login_required
def transactions():
    """交易记录管理页面"""
    if not hasattr(current_user, 'role'):
        flash('权限不足', 'error')
        return redirect(url_for('admin.login'))
    
    # 获取筛选参数
    transaction_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    query = Transaction.query
    
    if transaction_type != 'all':
        query = query.filter_by(transaction_type=transaction_type)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    # 分页
    transactions_pagination = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/transactions.html',
                         transactions=transactions_pagination.items,
                         pagination=transactions_pagination,
                         current_type=transaction_type,
                         current_status=status)

@admin.route('/api/stats')
@login_required
def api_stats():
    """API: 获取统计数据"""
    if not hasattr(current_user, 'role'):
        return jsonify({'error': '权限不足'}), 403
    
    # 基础统计
    stats = {
        'total_users': User.query.count(),
        'pending_users': User.query.filter_by(status='pending').count(),
        'active_users': User.query.filter_by(status='active').count(),
        'total_orders': Order.query.count(),
        'today_orders': Order.query.filter(
            db.func.date(Order.created_at) == datetime.utcnow().date()
        ).count()
    }
    
    # 最近7天的用户注册趋势
    user_trend = []
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = User.query.filter(db.func.date(User.created_at) == date).count()
        user_trend.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })
    
    stats['user_trend'] = list(reversed(user_trend))
    
    return jsonify(stats)

@admin.route('/api/user/<int:user_id>/toggle_status', methods=['POST'])
@login_required
def api_toggle_user_status(user_id):
    """API: 切换用户状态"""
    if not hasattr(current_user, 'role'):
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.status.value == 'active':
        user.status = 'disabled'
        message = f'用户 {user.username} 已禁用'
    else:
        user.status = 'active'
        message = f'用户 {user.username} 已启用'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': message,
        'new_status': user.status.value
    })

# 错误处理
@admin.errorhandler(403)
def forbidden(error):
    """403错误处理"""
    return render_template('admin/error.html', 
                         error_code=403,
                         error_message='权限不足，请使用管理员账号登录'), 403

@admin.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('admin/error.html',
                         error_code=404,
                         error_message='页面未找到'), 404

@admin.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    db.session.rollback()
    return render_template('admin/error.html',
                         error_code=500,
                         error_message='服务器内部错误'), 500 