# 智能卡路里分析系统

基于AI视觉技术的食物卡路里分析系统，集成完整的用户认证系统和管理后台。

## 功能特点

### 核心功能
- 🍎 **智能食物识别**：上传食物图片，AI自动识别食物类型
- 📊 **营养成分分析**：精准计算卡路里、蛋白质、脂肪、碳水化合物含量
- 📱 **响应式设计**：支持手机、平板、桌面设备
- 🎨 **现代化UI**：简洁美观的用户界面

### 用户系统
- 👤 **用户注册/登录**：完整的用户认证系统
- 🔐 **密码加密**：使用bcrypt安全存储密码
- 📝 **历史记录管理**：用户专属的分析历史记录
- 🔒 **数据隔离**：用户只能访问自己的数据

### 管理后台
- 👥 **用户管理**：查看、启用/禁用、删除用户
- 📊 **系统统计**：用户数量、分析次数等统计信息
- 🛡️ **权限控制**：管理员专用后台界面
- 📈 **数据监控**：实时监控系统使用情况

## 技术栈

- **后端**: Python Flask
- **数据库**: MongoDB
- **认证**: Flask-Session + bcrypt
- **AI服务**: Google Gemini API
- **前端**: HTML5 + CSS3 + JavaScript
- **图像处理**: Pillow (PIL)
- **部署**: Docker + Gunicorn

## 云端部署

本项目专为云端部署设计，使用Zeabur等云平台进行部署。

### Zeabur部署步骤

1. **连接GitHub仓库**
   - 在Zeabur控制台中连接此GitHub仓库
   - Zeabur会自动识别Dockerfile并构建应用

2. **添加MongoDB服务**
   - 在Zeabur项目中添加MongoDB服务
   - 系统会自动生成数据库连接信息

3. **配置环境变量**
   - 在Zeabur环境变量设置中添加以下配置

### 环境变量配置（仅需3个）

在Zeabur环境变量设置中配置以下3个变量：

#### 1. 数据库连接字符串（必需）
```
MONGODB_URI=mongodb://username:password@host:port
```

**常见范例：**
- **Zeabur原始连接**：`mongodb://mongo:password@hkg1.clusters.zeabur.com:30826`
- **MongoDB Atlas**：`mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/fitness_app?retryWrites=true&w=majority`
- **Railway插件**：`mongodb://mongo:password@containers-us-west-1.railway.app:27017`
- **本地MongoDB**：`mongodb://localhost:27017`

**✨ 智能特性：**
- 可以直接使用云平台提供的原始连接字符串
- 系统会自动添加默认数据库名 `fitness_app`
- 如果连接字符串已包含数据库名，保持不变

*注意：Zeabur等云平台会自动生成此变量，直接使用即可*

#### 2. Gemini AI API密钥（必需）
```
GEMINI_API_KEY=sk-your-aihubmix-api-key-here
```

#### 3. Gemini API基础URL（必需）
```
GEMINI_BASE_URL=https://aihubmix.com/gemini
```

**注意：** 应用密钥和管理员注册密钥已内置到代码中，无需配置。

## MONGODB_URI 详细配置指南

### 格式说明
```
mongodb://[username:password@]host[:port][/database][?options]
```
**注意：** 数据库名是可选的，系统会自动添加默认数据库名 `fitness_app`

### 各云平台获取方法

#### 🔵 Zeabur（推荐）
1. 在项目中点击"Add Service" → "Database" → "MongoDB"
2. MongoDB服务启动后，系统自动生成 `MONGODB_URI`
3. 在Web应用环境变量中自动出现，格式如：
   ```
   mongodb://mongo:randompassword@hkg1.clusters.zeabur.com:30826
   ```
4. **直接使用即可**，系统会自动添加数据库名 `fitness_app`

#### 🟢 Railway
1. 添加MongoDB插件
2. 插件自动生成连接字符串，格式如：
   ```
   mongodb://mongo:password@containers-us-west-1.railway.app:27017/railway
   ```

#### 🟣 MongoDB Atlas（适用于任何平台）
1. 注册 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)（有免费套餐）
2. 创建集群并获取连接字符串：
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/fitness_app?retryWrites=true&w=majority
   ```
3. 将此字符串配置到任何云平台的环境变量中

#### 🔴 Render
1. 创建MongoDB数据库服务或连接外部MongoDB
2. 获取连接字符串并配置到环境变量

### 连接字符串组成部分
- **协议**：`mongodb://` 或 `mongodb+srv://`（Atlas使用）
- **认证**：`username:password@`（如果需要认证）
- **主机**：`host:port`（服务器地址和端口）
- **数据库**：`/database_name`（可选，系统会自动添加 `fitness_app`）
- **选项**：`?retryWrites=true&w=majority`（可选参数）

### 🎯 推荐做法
**直接使用云平台提供的原始连接字符串**，例如：
```
# Zeabur提供的原始连接字符串
MONGODB_URI=mongodb://mongo:pZtU5lg1qv9jA7XLR280MwG4xVYPz36C@hkg1.clusters.zeabur.com:30826

# 系统会自动转换为：
# mongodb://mongo:pZtU5lg1qv9jA7XLR280MwG4xVYPz36C@hkg1.clusters.zeabur.com:30826/fitness_app
```

4. **部署应用**
   - 配置完成后，Zeabur会自动部署应用
   - 部署完成后会提供访问域名

## 详细部署步骤

### 1. 准备工作
- 确保代码已推送到GitHub仓库
- 准备Gemini API密钥

### 2. 创建Zeabur项目
1. 登录 [Zeabur控制台](https://zeabur.com)
2. 点击"New Project"创建新项目
3. 连接GitHub仓库

### 3. 添加服务

#### 添加MongoDB服务
1. 在项目中点击"Add Service"
2. 选择"Database" → "MongoDB"
3. 等待MongoDB服务启动完成

#### 添加Web应用
1. 点击"Add Service" → "Git Repository"
2. 选择你的GitHub仓库
3. Zeabur会自动识别Dockerfile并开始构建

### 4. 配置环境变量
在Web应用的"Environment"标签页中添加3个环境变量：
```
MONGODB_URI=<MongoDB服务自动生成>
GEMINI_API_KEY=sk-your-aihubmix-api-key-here
GEMINI_BASE_URL=https://aihubmix.com/gemini
```

### 5. 部署完成
- 配置完成后，Zeabur会自动重新部署应用
- 部署成功后，点击"Domain"获取访问域名
- 访问 `/auth/admin-register` 创建第一个管理员账号

## 使用说明

### 首次部署后的设置

1. **访问应用**: 使用Zeabur提供的域名访问应用
2. **创建管理员**: 访问 `/auth/admin-register` 创建第一个管理员账号
3. **管理员登录**: 使用创建的管理员账号登录系统
4. **系统测试**: 注册测试用户，验证功能正常

### 超级管理员注册流程

1. **访问注册页面**: 打开 `/auth/admin-register`
2. **填写信息**: 输入用户名、邮箱、密码和管理员注册密钥
3. **管理员密钥**: `H7jK9mN2pQ5rS8tU1vW4xY7zA0bC3dF6gH9jK2mN5pQ8rS1tU4vW7xY0zA3bC6dF`
4. **完成注册**: 注册成功后自动获得管理员权限
5. **统一登录**: 管理员和普通用户都使用 `/auth/login` 登录

### 用户功能

1. **注册账号**: 访问 `/auth/register` 创建新账号
2. **登录系统**: 访问 `/auth/login` 登录
3. **上传分析**: 登录后上传食物图片进行分析
4. **查看历史**: 查看个人的分析历史记录

### 管理员功能

1. **登录后台**: 使用管理员账号登录后访问 `/admin`
2. **用户管理**: 查看、管理所有用户账号
3. **系统统计**: 查看系统使用统计信息
4. **权限控制**: 启用/禁用用户账号

### 访问地址

- **主页**: `https://your-app.zeabur.app`
- **用户登录**: `https://your-app.zeabur.app/auth/login`
- **用户注册**: `https://your-app.zeabur.app/auth/register`
- **管理员注册**: `https://your-app.zeabur.app/auth/admin-register`
- **管理后台**: `https://your-app.zeabur.app/admin`

## API接口

### 认证接口
- `POST /auth/register` - 普通用户注册
- `POST /auth/admin-register` - 超级管理员注册
- `POST /auth/login` - 用户登录（统一入口）
- `POST /auth/logout` - 用户登出
- `GET /auth/current_user` - 获取当前用户信息

### 历史记录接口
- `GET /api/history/` - 获取用户历史记录
- `POST /api/history/` - 保存分析记录
- `DELETE /api/history/<id>` - 删除单条记录
- `POST /api/history/clear` - 清空历史记录

### 分析接口
- `POST /analyze` - 分析食物图片

## 数据库结构

### 用户集合 (users)
```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password": String, // bcrypt加密
  "is_active": Boolean,
  "is_admin": Boolean,
  "created_at": Date,
  "updated_at": Date
}
```

### 历史记录集合 (history)
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "image_data": String, // base64编码
  "analysis_result": String,
  "usage_info": Object,
  "created_at": Date
}
```

## 安全特性

- 🔐 **密码加密**: 使用bcrypt加密存储
- 🛡️ **会话管理**: 安全的用户会话控制
- 🔒 **数据隔离**: 用户数据严格隔离
- ⚡ **输入验证**: 完整的数据验证机制
- 🚫 **权限控制**: 基于角色的访问控制
- 🔑 **安全注册**: 管理员注册需要密钥验证
- 🎯 **统一认证**: 单一登录入口，自动权限识别

## 支持的图片格式

- PNG
- JPG/JPEG
- WEBP
- GIF
- BMP

最大文件大小：20MB

## 其他云平台部署

### Railway
1. 连接GitHub仓库
2. 添加MongoDB插件
3. 配置3个环境变量
4. 自动部署

### Render
1. 连接GitHub仓库
2. 选择Docker部署
3. 配置环境变量
4. 添加MongoDB数据库服务

## 部署后检查

### 1. 验证应用运行
- 访问主页，应该重定向到登录页面
- 尝试注册新用户
- 测试图片上传和分析功能

### 2. 创建管理员账号
- 访问 `/auth/admin-register` 页面
- 使用内置的管理员注册密钥
- 登录管理员账号并访问 `/admin` 管理后台
- 检查用户管理和统计功能

### 3. 安全检查
- 确认环境变量配置正确
- 检查HTTPS是否正常工作
- 测试普通用户注册和登录功能

## 常见问题

### 部署失败
- 检查Dockerfile是否正确
- 确认所有依赖都在requirements.txt中
- 查看构建日志排查错误

### 数据库连接失败
- 确认MongoDB服务已启动
- 检查MONGODB_URI环境变量是否正确
- 确认网络连接正常

### API调用失败
- 验证Gemini API密钥是否正确
- 检查API配额是否充足
- 确认网络访问正常

## 监控和维护

### 日志查看
- 在云平台控制台查看应用日志
- 监控错误和异常信息
- 关注性能指标

### 数据备份
- 定期导出MongoDB数据
- 备份重要配置信息
- 制定灾难恢复计划

### 更新部署
- 推送代码到GitHub
- 云平台会自动触发重新部署
- 监控部署状态和应用健康

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License