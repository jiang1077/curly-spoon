from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import enum

class UserStatus(enum.Enum):
    """用户状态枚举"""
    PENDING = "pending"      # 待审核
    ACTIVE = "active"        # 正常
    DISABLED = "disabled"    # 禁用

class OrderDirection(enum.Enum):
    """交易方向枚举"""
    UP = "up"     # 看涨
    DOWN = "down" # 看跌

class OrderResult(enum.Enum):
    """交易结果枚举"""
    PENDING = "pending"  # 进行中
    WIN = "win"         # 盈利
    LOSE = "lose"       # 亏损

class TransactionType(enum.Enum):
    """交易类型枚举"""
    DEPOSIT = "deposit"       # 充值
    WITHDRAWAL = "withdrawal" # 提现
    TRADE = "trade"          # 交易
    BONUS = "bonus"          # 奖励

class TransactionStatus(enum.Enum):
    """交易状态枚举"""
    PENDING = "pending"      # 等待中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消

class ProfitControl(enum.Enum):
    """盈利控制枚举"""
    SUCCESS = "success"  # 必胜
    FAIL = "fail"       # 必败
    RANDOM = "random"   # 随机

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # 资金相关
    balance = db.Column(db.Decimal(15, 2), default=0.00)
    fund_password_hash = db.Column(db.String(128))  # 资金密码
    
    # 状态和等级
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING)
    vip_level = db.Column(db.Integer, default=0)
    
    # 证件信息（根据修改后的规划）
    id_card_front = db.Column(db.String(255))  # 证件正面
    id_card_back = db.Column(db.String(255))   # 证件反面
    real_name = db.Column(db.String(100))      # 真实姓名
    id_number = db.Column(db.String(50))       # 证件号码
    
    # 盈利控制（新增）
    profit_control = db.Column(db.Enum(ProfitControl), default=ProfitControl.RANDOM)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置登录密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证登录密码"""
        return check_password_hash(self.password_hash, password)
    
    def set_fund_password(self, password):
        """设置资金密码"""
        self.fund_password_hash = generate_password_hash(password)
    
    def check_fund_password(self, password):
        """验证资金密码"""
        if not self.fund_password_hash:
            return False
        return check_password_hash(self.fund_password_hash, password)
    
    def get_available_balance(self):
        """获取可用余额"""
        # 减去进行中的交易金额
        pending_orders = Order.query.filter_by(
            user_id=self.id, 
            result=OrderResult.PENDING
        ).all()
        frozen_amount = sum(order.amount for order in pending_orders)
        return float(self.balance) - frozen_amount
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(UserMixin, db.Model):
    """管理员模型"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # 权限和角色
    role = db.Column(db.String(20), default='admin')  # super_admin, admin
    permissions = db.Column(db.Text)  # JSON格式的权限配置
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        """检查是否为超级管理员"""
        return self.role == 'super_admin'
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class Order(db.Model):
    """交易订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 交易信息
    symbol = db.Column(db.String(20), nullable=False)  # 交易对，如BTC/USDT
    direction = db.Column(db.Enum(OrderDirection), nullable=False)
    amount = db.Column(db.Decimal(15, 2), nullable=False)  # 投注金额
    
    # 期权信息
    duration = db.Column(db.Integer, nullable=False)  # 时长（秒）
    profit_rate = db.Column(db.Decimal(5, 4), nullable=False)  # 收益率
    
    # 价格信息
    start_price = db.Column(db.Decimal(15, 8))  # 开始价格
    end_price = db.Column(db.Decimal(15, 8))    # 结束价格
    
    # 结果
    result = db.Column(db.Enum(OrderResult), default=OrderResult.PENDING)
    profit_amount = db.Column(db.Decimal(15, 2), default=0.00)  # 盈利金额
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime, nullable=False)
    settled_at = db.Column(db.DateTime)  # 结算时间
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if self.expired_at is None and self.duration:
            self.expired_at = datetime.utcnow() + timedelta(seconds=self.duration)
    
    def is_expired(self):
        """检查是否已到期"""
        return datetime.utcnow() >= self.expired_at
    
    def calculate_profit(self):
        """计算盈利金额"""
        if self.result == OrderResult.WIN:
            return float(self.amount) * float(self.profit_rate)
        return 0.0
    
    def __repr__(self):
        return f'<Order {self.id}: {self.symbol} {self.direction.value}>'

class Transaction(db.Model):
    """资金记录模型"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 交易信息
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Decimal(15, 2), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # 详细信息
    description = db.Column(db.String(255))
    tx_hash = db.Column(db.String(128))  # 区块链交易哈希（如果适用）
    wallet_address = db.Column(db.String(128))  # 钱包地址（充值/提现）
    network = db.Column(db.String(20))  # 网络类型（TRC20, ERC20等）
    
    # 手续费信息
    fee_amount = db.Column(db.Decimal(15, 2), default=0.00)
    fee_rate = db.Column(db.Decimal(5, 4), default=0.00)
    
    # 关联订单（如果是交易相关）
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.type.value} {self.amount}>'

class MarketPrice(db.Model):
    """市场价格模型"""
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    price = db.Column(db.Decimal(15, 8), nullable=False)
    change_24h = db.Column(db.Decimal(8, 4))  # 24小时涨跌幅
    volume_24h = db.Column(db.Decimal(20, 2))  # 24小时交易量
    
    # 时间戳
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @classmethod
    def get_latest_price(cls, symbol):
        """获取最新价格"""
        return cls.query.filter_by(symbol=symbol).order_by(cls.timestamp.desc()).first()
    
    def __repr__(self):
        return f'<MarketPrice {self.symbol}: {self.price}>'

class SystemSettings(db.Model):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        """获取设置值"""
        setting = cls.query.get(key)
        return setting.value if setting else default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """设置值"""
        setting = cls.query.get(key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value}>'

class UserLoginLog(db.Model):
    """用户登录日志"""
    __tablename__ = 'user_login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))  # 支持IPv6
    user_agent = db.Column(db.String(255))
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserLoginLog {self.user_id}: {self.ip_address}>' 