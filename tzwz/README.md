# CoinBit 数字期权交易平台

## 项目概述

CoinBit是一个专业的数字期权交易平台，专注于**简洁、流畅、稳定**的设计理念。平台支持多语言（14种语言）、移动优先设计，提供完整的期权交易功能。

## ⭐ 已完成功能

### 第一阶段：基础架构和认证系统 ✅

#### 1. 技术栈配置
- ✅ Flask后端框架
- ✅ MySQL数据库
- ✅ Flask-Login用户认证
- ✅ Flask-Babel多语言支持
- ✅ Bootstrap 5前端UI
- ✅ 响应式移动优先设计

#### 2. 数据库设计
- ✅ 用户表（User）：包含证件验证字段
- ✅ 管理员表（Admin）：支持超级管理员和普通管理员
- ✅ 订单表（Order）：期权交易订单
- ✅ 交易记录表（Transaction）：资金流水记录
- ✅ 市场价格表（MarketPrice）：实时价格数据
- ✅ 系统设置表（SystemSettings）：配置管理
- ✅ 登录日志表（UserLoginLog）：安全审计

#### 3. 核心功能模块
- ✅ 用户注册/登录系统
- ✅ 证件上传验证（身份证正反面）
- ✅ 多语言支持（14种语言）
- ✅ 个人中心和账户设置
- ✅ 实时价格显示系统
- ✅ WhatsApp客服集成

#### 4. 前端界面
- ✅ 深色主题设计（#1a1a1a背景）
- ✅ 橙色主色调（#FF9500）
- ✅ 移动端底部导航
- ✅ 响应式布局
- ✅ 实时价格更新
- ✅ Flash消息系统

## 🎯 核心特性

### 用户注册流程（根据最新规划）
1. **邮箱注册** - 用户使用邮箱和密码注册
2. **证件上传** - 上传身份证正反面照片
3. **管理员审核** - 后台管理员审核证件
4. **账户激活** - 审核通过后用户可正常交易

### 交易参数配置
- 60s期权：1分钟到期，+10%收益率
- 90s期权：1.5分钟到期，+15%收益率
- 120s期权：2分钟到期，+25%收益率
- 180s期权：3分钟到期，+35%收益率
- 240s期权：4分钟到期，+50%收益率
- 300s期权：5分钟到期，+80%收益率

### 资金配置
- 最小充值：1 USDT
- 最小提现：5 USDT
- 提现手续费：10%
- 支持币种：USDT-TRC20（推荐）、USDT-ERC20

### 管理员控制系统
- 用户盈利控制：必胜/必败/随机（3种模式）
- 用户余额管理：超级管理员可直接修改
- 证件审核：管理员审核用户上传的证件
- WhatsApp客服号码：后台可配置

## 📱 多语言支持

支持14种语言，包括：
- 中文 (zh)
- English (en)
- 日本語 (ja)
- 한국어 (ko)
- Español (es)
- Français (fr)
- Deutsch (de)
- Русский (ru)
- Português (pt)
- Italiano (it)
- Nederlands (nl)
- Türkçe (tr)
- العربية (ar) - 支持RTL布局
- हिन्दी (hi)

## 🛠️ 安装和运行

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis（可选，用于缓存）

### 安装步骤
1. **克隆项目**
```bash
git clone <repository_url>
cd tzwz
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 创建.env文件
cp .env.example .env
# 编辑配置信息
```

4. **初始化数据库**
```bash
python app.py init_db
python app.py deploy
```

5. **创建管理员账户**
```bash
python app.py create_admin
```

6. **启动应用**
```bash
python app.py
```

访问：http://localhost:5000

## 📁 项目结构

```
tzwz/
├── app/                    # 应用包
│   ├── __init__.py        # 应用工厂
│   ├── models.py          # 数据库模型
│   ├── forms.py           # 表单类
│   ├── main/              # 主要路由
│   ├── auth/              # 认证路由
│   ├── trading/           # 交易路由（待开发）
│   ├── wallet/            # 钱包路由（待开发）
│   └── admin/             # 管理员路由（待开发）
├── templates/             # HTML模板
│   ├── base.html         # 基础模板
│   ├── main/             # 主要页面模板
│   └── auth/             # 认证页面模板
├── static/               # 静态文件
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript文件
│   └── uploads/          # 上传文件目录
├── config.py             # 配置文件
├── requirements.txt      # 依赖列表
└── app.py               # 应用入口
```

## 🚀 下一步开发计划

### 第二阶段：交易系统开发
- [ ] 创建交易路由和模板
- [ ] 实时价格API集成
- [ ] 订单创建和管理
- [ ] 交易结果计算
- [ ] 订单历史查询

### 第三阶段：钱包系统开发
- [ ] 充值功能（USDT地址生成）
- [ ] 提现功能（地址验证）
- [ ] 资金流水记录
- [ ] 余额管理

### 第四阶段：管理后台开发
- [ ] 用户管理界面
- [ ] 交易控制面板
- [ ] 系统设置管理
- [ ] 统计报表功能

## 🎨 设计特色

### 视觉设计
- **深色主题**：专业的交易界面体验
- **橙色主色调**：活力和信任感的体现
- **移动优先**：完美适配各种设备
- **简洁流畅**：避免复杂和多余的元素

### 用户体验
- **快速注册**：简化的注册流程
- **实时价格**：10秒自动更新价格
- **直观交易**：一键选择方向和时长
- **24/7客服**：WhatsApp即时联系

## 🔒 安全特性

- 密码加密存储（bcrypt）
- CSRF保护
- 会话管理
- 文件上传安全验证
- 登录日志记录
- IP地址跟踪

## 📞 技术支持

如果您在使用过程中遇到问题，请通过以下方式联系：
- WhatsApp：+1234567890（可在后台配置）
- 邮箱：support@coinbit.com

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 完成基础架构搭建
- ✅ 实现用户注册/登录系统
- ✅ 添加证件上传验证功能
- ✅ 集成多语言支持
- ✅ 创建响应式前端界面
- ✅ 实现实时价格显示

### 即将发布
- 🔄 交易系统开发中
- 🔄 钱包功能开发中
- 🔄 管理后台开发中

---

**CoinBit** - 专业的数字期权交易平台，让交易更简单！ 