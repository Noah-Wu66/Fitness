# 智能卡路里分析系统

基于AI视觉技术的食物卡路里分析系统，集成完整的用户认证系统和管理后台。

## 功能特点

### 核心功能
- 🍎 **智能食物识别**：上传食物图片，AI自动识别食物类型
- 📊 **营养成分分析**：精准计算卡路里、蛋白质、脂肪、碳水化合物含量
- 🎯 **个性化热量目标**：根据用户身体数据计算每日热量需求
- 📈 **热量仪表盘**：实时显示每日热量摄入进度
- 👤 **用户信息管理**：完整的个人信息设置和管理
- 📱 **响应式设计**：支持手机、平板、桌面设备
- 🎨 **现代化UI**：简洁美观的用户界面

### 用户系统
- 👤 **用户注册/登录**：完整的用户认证系统
- 🔐 **密码加密**：使用bcrypt安全存储密码
- 📝 **历史记录管理**：用户专属的分析历史记录
- 🔒 **数据隔离**：用户只能访问自己的数据
- ⚙️ **个人信息设置**：分步骤的用户信息收集流程
- 🎯 **智能热量计算**：基于Harris-Benedict公式的热量需求计算
- 📊 **个人中心**：完整的用户信息管理和编辑功能

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

## 🎯 个性化热量系统

### 用户信息收集流程
- **分步骤表单**：友好的两步式信息收集流程
  - 第一步：基本信息（昵称、性别、年龄、身高、体重）
  - 第二步：目标设定（目标体重、目标类型、活动水平）
- **智能验证**：实时表单验证和错误提示
- **进度指示**：清晰的进度条和步骤指示器

### 科学热量计算
- **Harris-Benedict公式**：科学准确的基础代谢率计算
  - 男性：BMR = 88.362 + (13.397 × 体重kg) + (4.799 × 身高cm) - (5.677 × 年龄)
  - 女性：BMR = 447.593 + (9.247 × 体重kg) + (3.098 × 身高cm) - (4.330 × 年龄)
- **活动水平调整**：5个活动水平选项，精确计算总热量需求
  - 久坐不动：BMR × 1.2
  - 轻度活动：BMR × 1.375
  - 中度活动：BMR × 1.55
  - 高度活动：BMR × 1.725
  - 极高活动：BMR × 1.9
- **目标导向**：根据减重/维持/增重目标自动调整热量建议
- **安全下限**：确保热量不低于基础代谢率的80%

### 实时热量仪表盘
- **可视化进度**：圆形进度条和百分比显示
- **智能颜色提示**：
  - 白色：正常进度（0-80%）
  - 黄色：接近目标（80-100%）
  - 红色：超出目标（>100%）
- **实时数据**：当前热量摄入、目标热量、剩余热量
- **自动更新**：分析食物后自动更新热量数据
- **平滑动画**：数值变化时的缩放动画效果

### 用户中心功能
- **完整资料管理**：查看和编辑所有个人信息
- **健康数据统计**：BMI指数、热量目标、活动水平
- **头像系统**：支持头像上传和更换
- **实时重算**：信息修改后立即重新计算热量目标

### 移动端完美适配
- **响应式设计**：完美适配手机、平板、桌面设备
- **触摸友好**：按钮大小符合移动端触摸标准（最小44px）
- **手势支持**：支持拖拽上传和滑动操作
- **横竖屏适配**：自动适应设备方向变化

### 现代化UI设计
- **渐变背景**：美观的渐变色彩搭配
- **卡片布局**：清晰的信息层次和视觉分组
- **微交互动画**：按钮点击、页面切换的平滑动画
- **加载状态**：友好的加载动画和进度提示
- **深色模式**：自动适应系统深色模式偏好
- **无障碍访问**：完整的键盘导航和焦点管理

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
- `GET /auth/setup-profile` - 用户信息设置页面
- `POST /auth/setup-profile` - 保存用户信息设置

### 历史记录接口
- `GET /api/history/` - 获取用户历史记录
- `POST /api/history/` - 保存分析记录
- `DELETE /api/history/<id>` - 删除单条记录
- `POST /api/history/clear` - 清空历史记录

### 用户信息接口
- `GET /user-center` - 用户中心页面
- `GET /api/user/profile` - 获取用户完整信息
- `PUT /api/user/profile` - 更新用户信息
- `GET /api/user/calorie-goal` - 获取用户每日热量目标

### 分析接口
- `POST /analyze` - 分析食物图片

## 数据库结构

### 用户表 (users)
```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password": String, // bcrypt加密
  "is_active": Boolean,
  "is_admin": Boolean,
  "created_at": Date,
  "updated_at": Date,
  "profile": {
    "nickname": String,
    "gender": String, // "male" | "female"
    "age": Number,
    "height": Number, // 厘米
    "weight": Number, // 公斤
    "target_weight": Number, // 目标体重（公斤）
    "avatar": String, // 头像URL
    "daily_calorie_goal": Number, // 每日热量目标
    "activity_level": String, // "sedentary" | "light" | "moderate" | "active" | "very_active"
    "goal_type": String // "lose" | "maintain" | "gain"
  },
  "profile_completed": Boolean
}
```

### 历史记录表 (history)

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

### 2. 验证新功能
- **用户信息收集**：新用户登录后应自动跳转到信息设置页面
- **热量仪表盘**：主页应显示个性化热量仪表盘
- **用户中心**：点击"个人中心"链接，验证信息管理功能
- **移动端适配**：在手机浏览器中测试响应式设计
- **热量计算**：完成信息设置后验证热量目标计算是否正确

### 3. 创建管理员账号
- 访问 `/auth/admin-register` 页面
- 使用内置的管理员注册密钥
- 登录管理员账号并访问 `/admin` 管理后台
- 检查用户管理和统计功能

### 4. 安全检查
- 确认环境变量配置正确
- 检查HTTPS是否正常工作
- 测试普通用户注册和登录功能

### 5. 功能完整性检查
- [ ] 用户注册/登录正常
- [ ] 首次登录自动跳转到信息设置
- [ ] 信息设置表单验证正常
- [ ] 两步式信息收集流程完整（已修复无限循环Bug）
- [ ] 热量计算结果合理
- [ ] 热量仪表盘显示正确
- [ ] 食物分析后热量自动更新
- [ ] 用户中心信息编辑功能正常
- [ ] 移动端界面适配良好
- [ ] 所有动画效果正常

### 6. 已知问题修复
- ✅ **用户信息设置无限循环Bug**：修复了用户完成信息设置后无法进入主页的问题
  - 修复了Session管理不完整的问题
  - 改进了前端表单数据收集逻辑
  - 强化了后端数据验证和处理

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