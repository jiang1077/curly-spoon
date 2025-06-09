# CoinBit数字期权交易平台 - 数据库设置指南

## 📊 数据库架构概述

CoinBit平台使用MySQL数据库，包含以下核心表结构：

### 🏗️ 数据库表结构

1. **用户相关表**
   - `users` - 用户基本信息、余额、状态
   - `user_login_logs` - 用户登录日志

2. **管理相关表**
   - `admins` - 管理员账户和权限

3. **交易相关表**
   - `orders` - 数字期权交易订单
   - `transactions` - 资金交易记录（充值/提现）

4. **系统相关表**
   - `market_prices` - 市场价格数据
   - `system_settings` - 系统配置参数

## 🚀 快速部署步骤

### 第一步：安装MySQL

**Windows:**
```bash
# 下载并安装MySQL Community Server
# 或使用XAMPP/WAMP集成环境
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 第二步：创建数据库

1. **登录MySQL:**
```bash
mysql -u root -p
```

2. **运行数据库创建脚本:**
```sql
source create_mysql_database.sql;
```

或手动执行：
```sql
-- 创建数据库
CREATE DATABASE coinbit_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'coinbit_user'@'localhost' IDENTIFIED BY 'coinbit_password_2024';

-- 授予权限
GRANT ALL PRIVILEGES ON coinbit_dev.* TO 'coinbit_user'@'localhost';
FLUSH PRIVILEGES;
```

### 第三步：安装Python依赖

```bash
pip install -r requirements.txt
```

### 第四步：测试数据库连接

```bash
python database_test.py
```

### 第五步：初始化数据库

```bash
python init_database.py
```

## 🔧 配置说明

### 数据库连接配置

在 `config.py` 中配置数据库连接：

```python
# 开发环境
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_dev?charset=utf8mb4'

# 生产环境
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_db?charset=utf8mb4'
```

### 环境变量配置

创建 `.env` 文件（可选）：
```env
DATABASE_URL=mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_dev?charset=utf8mb4
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here
```

## 📋 默认数据

初始化后将创建以下默认数据：

### 🔑 管理员账户
- **超级管理员**: admin / admin123
- **普通管理员**: manager / manager123

### 👥 测试用户
- **用户1**: user001 / password123 (余额: $1,250.50)
- **用户2**: trader123 / password123 (余额: $3,780.25)
- **用户3**: crypto_fan / password123 (余额: $520.80)

### 📈 市场数据
- BTC/USDT: $43,500.00
- ETH/USDT: $2,420.50
- LTC/USDT: $75.25
- XRP/USDT: $0.485

## 🚨 故障排除

### 常见问题

1. **连接被拒绝 (Connection refused)**
   ```bash
   # 检查MySQL服务状态
   sudo systemctl status mysql
   
   # 启动MySQL服务
   sudo systemctl start mysql
   ```

2. **Access denied for user**
   ```sql
   -- 重新创建用户和权限
   DROP USER IF EXISTS 'coinbit_user'@'localhost';
   CREATE USER 'coinbit_user'@'localhost' IDENTIFIED BY 'coinbit_password_2024';
   GRANT ALL PRIVILEGES ON coinbit_dev.* TO 'coinbit_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **字符集问题**
   ```sql
   -- 确保数据库使用utf8mb4字符集
   ALTER DATABASE coinbit_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. **依赖包安装失败**
   ```bash
   # 更新pip
   pip install --upgrade pip
   
   # 单独安装问题包
   pip install pymysql
   pip install cryptography
   ```

### 🔍 调试工具

1. **数据库连接测试**
   ```bash
   python database_test.py
   ```

2. **查看数据库状态**
   ```bash
   python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print(db.engine.execute('SHOW TABLES').fetchall())"
   ```

3. **重置数据库**
   ```bash
   python init_database.py  # 会清空并重新创建所有表
   ```

## 📊 数据库监控

### 性能优化建议

1. **创建索引**
   ```sql
   -- 为常用查询字段创建索引
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_orders_user_id ON orders(user_id);
   CREATE INDEX idx_orders_created_at ON orders(created_at);
   ```

2. **连接池配置**
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 10,        # 连接池大小
       'pool_recycle': 120,    # 连接回收时间
       'pool_pre_ping': True   # 连接预检
   }
   ```

## 🔄 数据库迁移

使用Flask-Migrate管理数据库版本：

```bash
# 初始化迁移
flask db init

# 创建迁移文件
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade
```

## 🔐 安全建议

1. **生产环境配置**
   - 使用强密码
   - 限制数据库用户权限
   - 启用SSL连接
   - 定期备份数据

2. **备份策略**
   ```bash
   # 每日备份
   mysqldump -u coinbit_user -p coinbit_db > backup_$(date +%Y%m%d).sql
   ```

## 📞 技术支持

如遇问题，请检查：
1. MySQL服务是否运行
2. 数据库连接配置是否正确
3. 用户权限是否足够
4. Python依赖是否完整安装

---

**🎯 完成部署后，访问:**
- 前台: http://localhost:5000
- 后台: http://localhost:5000/admin
- 使用 admin/admin123 登录后台管理系统 