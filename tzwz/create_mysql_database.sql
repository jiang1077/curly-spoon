-- CoinBit数字期权交易平台 - MySQL数据库创建脚本
-- 请在MySQL中以root用户身份运行此脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS coinbit_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建开发数据库
CREATE DATABASE IF NOT EXISTS coinbit_dev 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS coinbit_test 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建数据库用户（如果不存在）
CREATE USER IF NOT EXISTS 'coinbit_user'@'localhost' IDENTIFIED BY 'coinbit_password_2024';

-- 授予权限
GRANT ALL PRIVILEGES ON coinbit_db.* TO 'coinbit_user'@'localhost';
GRANT ALL PRIVILEGES ON coinbit_dev.* TO 'coinbit_user'@'localhost';
GRANT ALL PRIVILEGES ON coinbit_test.* TO 'coinbit_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示创建的数据库
SHOW DATABASES LIKE 'coinbit%';

-- 显示用户权限
SHOW GRANTS FOR 'coinbit_user'@'localhost';

-- 使用说明
/*
执行步骤:
1. 使用MySQL root用户登录: mysql -u root -p
2. 运行此脚本: source create_mysql_database.sql;
3. 退出MySQL: exit;
4. 修改config.py中的数据库连接字符串为:
   'mysql+pymysql://coinbit_user:coinbit_password_2024@localhost/coinbit_dev?charset=utf8mb4'
5. 运行数据库初始化: python init_database.py
*/ 