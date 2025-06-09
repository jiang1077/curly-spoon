from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Optional
from app.models import User, Admin

class LoginForm(FlaskForm):
    """用户登录表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ], render_kw={'placeholder': '请输入邮箱地址'})
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ], render_kw={'placeholder': '请输入密码'})
    
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20字符之间')
    ], render_kw={'placeholder': '请输入用户名'})
    
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ], render_kw={'placeholder': '请输入邮箱地址'})
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, message='密码长度至少6位')  # 根据修改后的规划：6位以上
    ], render_kw={'placeholder': '请输入密码（至少6位）'})
    
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ], render_kw={'placeholder': '请再次输入密码'})
    
    invite_code = StringField('邀请码（可选）', validators=[
        Optional()
    ], render_kw={'placeholder': '请输入邀请码（可选）'})
    
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        """验证用户名唯一性"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被注册，请选择其他用户名')
    
    def validate_email(self, email):
        """验证邮箱唯一性"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

class IDCardUploadForm(FlaskForm):
    """证件上传表单 - 根据修改后的规划"""
    real_name = StringField('真实姓名', validators=[
        DataRequired(message='请输入真实姓名'),
        Length(min=2, max=50, message='姓名长度在2-50字符之间')
    ], render_kw={'placeholder': '请输入证件上的真实姓名'})
    
    id_number = StringField('证件号码', validators=[
        DataRequired(message='请输入证件号码'),
        Length(min=15, max=25, message='请输入有效的证件号码')
    ], render_kw={'placeholder': '请输入身份证/护照号码'})
    
    id_card_front = FileField('证件正面', validators=[
        FileRequired(message='请上传证件正面照片'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='只支持JPG、JPEG、PNG格式的图片')
    ])
    
    id_card_back = FileField('证件反面', validators=[
        FileRequired(message='请上传证件反面照片'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='只支持JPG、JPEG、PNG格式的图片')
    ])
    
    submit = SubmitField('提交审核')

class TradingForm(FlaskForm):
    """交易表单"""
    symbol = SelectField('交易对', choices=[
        ('BTC/USDT', 'BTC/USDT'),
        ('ETH/USDT', 'ETH/USDT'),
        ('LTC/USDT', 'LTC/USDT'),
        ('XRP/USDT', 'XRP/USDT')
    ], validators=[DataRequired()])
    
    direction = SelectField('交易方向', choices=[
        ('up', '看涨 (UP)'),
        ('down', '看跌 (DOWN)')
    ], validators=[DataRequired()])
    
    amount = DecimalField('投注金额', validators=[
        DataRequired(message='请输入投注金额'),
        NumberRange(min=1, max=10000, message='投注金额必须在1-10000之间')
    ], render_kw={'placeholder': '请输入投注金额', 'step': '0.01'})
    
    duration = SelectField('时长', choices=[
        (60, '60s (+10%)'),
        (90, '90s (+15%)'),
        (120, '120s (+25%)'),
        (180, '180s (+35%)'),
        (240, '240s (+50%)'),
        (300, '300s (+80%)')
    ], coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('确认交易')

class DepositForm(FlaskForm):
    """充值表单"""
    currency = SelectField('充值币种', choices=[
        ('USDT-TRC20', 'USDT (TRC20) - 推荐'),
        ('USDT-ERC20', 'USDT (ERC20)')
    ], validators=[DataRequired()])
    
    amount = DecimalField('充值金额', validators=[
        DataRequired(message='请输入充值金额'),
        NumberRange(min=1, message='最小充值金额为1 USDT')
    ], render_kw={'placeholder': '请输入充值金额', 'step': '0.01'})
    
    submit = SubmitField('生成充值地址')

class WithdrawForm(FlaskForm):
    """提现表单 - 根据修改后的规划"""
    amount = DecimalField('提现金额', validators=[
        DataRequired(message='请输入提现金额'),
        NumberRange(min=5, message='最小提现金额为5 USDT')  # 根据修改后的规划
    ], render_kw={'placeholder': '请输入提现金额（最少5 USDT）', 'step': '0.01'})
    
    wallet_address = StringField('提现地址', validators=[
        DataRequired(message='请输入提现地址'),
        Length(min=20, max=100, message='请输入有效的钱包地址')
    ], render_kw={'placeholder': '请输入USDT钱包地址'})
    
    network = SelectField('网络类型', choices=[
        ('TRC20', 'TRC20'),
        ('ERC20', 'ERC20')
    ], validators=[DataRequired()])
    
    fund_password = PasswordField('资金密码', validators=[
        DataRequired(message='请输入资金密码')
    ], render_kw={'placeholder': '请输入资金密码'})
    
    submit = SubmitField('申请提现')

class AdminLoginForm(FlaskForm):
    """管理员登录表单"""
    username = StringField('管理员账号', validators=[
        DataRequired(message='请输入管理员账号')
    ], render_kw={'placeholder': '请输入管理员用户名'})
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ], render_kw={'placeholder': '请输入管理员密码'})
    
    remember_me = BooleanField('记住登录')
    submit = SubmitField('登录')

class UserManageForm(FlaskForm):
    """用户管理表单"""
    user_id = HiddenField('用户ID', validators=[DataRequired()])
    
    status = SelectField('用户状态', choices=[
        ('pending', '待审核'),
        ('active', '正常'),
        ('disabled', '禁用')
    ], validators=[DataRequired()])
    
    balance = DecimalField('余额', validators=[
        NumberRange(min=0, message='余额不能为负数')
    ], render_kw={'step': '0.01'})
    
    profit_control = SelectField('盈利控制', choices=[
        ('random', '随机'),
        ('success', '必胜'),
        ('fail', '必败')
    ], validators=[DataRequired()])
    
    submit = SubmitField('保存修改')

class ProfileForm(FlaskForm):
    """个人资料表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20字符之间')
    ])
    
    current_password = PasswordField('当前密码', validators=[
        Optional()
    ], render_kw={'placeholder': '如要修改密码请输入当前密码'})
    
    new_password = PasswordField('新密码', validators=[
        Optional(),
        Length(min=6, message='新密码长度至少6位')
    ], render_kw={'placeholder': '请输入新密码（至少6位）'})
    
    confirm_password = PasswordField('确认新密码', validators=[
        EqualTo('new_password', message='两次输入的密码不一致')
    ], render_kw={'placeholder': '请再次输入新密码'})
    
    fund_password = PasswordField('设置资金密码', validators=[
        Optional(),
        Length(min=6, message='资金密码长度至少6位')
    ], render_kw={'placeholder': '请设置资金密码（用于提现）'})
    
    submit = SubmitField('保存修改')

class SystemSettingsForm(FlaskForm):
    """系统设置表单"""
    site_name = StringField('网站名称', validators=[
        DataRequired(message='请输入网站名称')
    ])
    
    announcement = TextAreaField('系统公告', validators=[
        DataRequired(message='请输入系统公告')
    ], render_kw={'rows': 3})
    
    whatsapp_number = StringField('WhatsApp客服号码', validators=[
        DataRequired(message='请输入WhatsApp号码')
    ], render_kw={'placeholder': '+1234567890'})
    
    maintenance_mode = BooleanField('维护模式')
    
    submit = SubmitField('保存设置') 