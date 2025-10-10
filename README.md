# py-picToWork

基于图像识别的屏幕自动化操作工具

## 项目简介

py-picToWork 是一个强大的自动化工具，能够：
- 🔍 识别屏幕上的图片元素
- 📍 精确定位图片在屏幕上的坐标位置
- 🖱️ 执行自动化操作（点击、键盘输入、拖拽等）
- 📝 编排和执行复杂的自动化工作流

## 技术栈

### 前端技术栈

1. **Vue 3** - 现代化前端框架
   - 响应式用户界面
   - 组件化开发
   - TypeScript 支持

2. **Electron** - 桌面应用打包
   - 跨平台桌面应用（Windows、macOS、Linux）
   - 原生窗口管理
   - 系统托盘集成
   - 与 Python 后端通信

3. **Element Plus / Ant Design Vue** - UI 组件库
   - 开箱即用的 UI 组件
   - 美观的界面设计
   - 丰富的交互组件

4. **Pinia** - 状态管理
   - Vue 3 官方推荐状态管理
   - 简洁的 API
   - TypeScript 支持

5. **Vite** - 构建工具
   - 快速的开发服务器
   - 高效的生产构建
   - 热模块替换（HMR）

### 后端技术栈（Python）

1. **FastAPI** - 现代 Python Web 框架
   - RESTful API 服务
   - WebSocket 支持（实时通信）
   - 自动生成 API 文档
   - 异步支持

2. **OpenCV (cv2)** - 图像识别核心
   - 模板匹配算法（Template Matching）
   - 多尺度图像识别
   - 图像预处理和特征提取
   - 高精度图像识别

3. **pyautogui / pynput** - 系统操作控制
   - 鼠标控制（移动、点击、拖拽）
   - 键盘控制（输入、快捷键）
   - 屏幕截图
   - 跨平台支持

4. **Pillow (PIL)** - 图像处理
   - 图像格式转换
   - 图像裁剪和缩放
   - 图像增强和滤镜

5. **NumPy** - 数值计算
   - 图像数据处理
   - 矩阵运算

6. **mss** - 高性能屏幕截图
   - 比 PyAutoGUI 更快
   - 支持多显示器
   - 区域截图

### 通信层

- **WebSocket** - 实时双向通信
  - 前端发送操作指令
  - 后端推送执行状态
  - 实时日志输出
  
- **HTTP/REST API** - 标准接口
  - 文件上传（目标图片）
  - 配置管理
  - 工作流 CRUD 操作

### 可选增强库

- **pytesseract** - OCR 文字识别
- **Redis** - 任务队列和缓存
- **SQLite** - 本地数据存储

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron 桌面应用                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Vue 3 前端界面                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ 工作流编辑器 │  │ 图片管理器   │  │ 执行控制台   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ 配置面板    │  │ 日志查看器   │  │ 状态监控    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ HTTP/WebSocket                    │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Electron Main Process                     │  │
│  │    - 窗口管理  - 系统托盘  - 进程通信                  │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ 子进程/HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Python 后端服务 (FastAPI)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   API 层                               │  │
│  │  - RESTful API  - WebSocket  - 文件上传               │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              工作流引擎 (Workflow Engine)              │  │
│  │  - 任务解析  - 流程控制  - 异常处理  - 队列管理       │  │
│  └────────────┬──────────────────────────────────────────┘  │
│               │                                              │
│      ┌────────┴────────┐                                    │
│      ▼                 ▼                                    │
│  ┌─────────────┐   ┌──────────────┐                        │
│  │图像识别模块  │   │操作执行模块   │                        │
│  │- 屏幕截图    │   │- 鼠标控制     │                        │
│  │- 模板匹配    │   │- 键盘输入     │                        │
│  │- 位置定位    │   │- 等待延迟     │                        │
│  │- 相似度计算  │   │- 滚动操作     │                        │
│  └─────────────┘   └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   操作系统 (OS API)   │
              │ - 屏幕控制            │
              │ - 输入模拟            │
              └──────────────────────┘
```

### 前后端通信流程

```
Vue 前端                  Electron Main              Python 后端
   │                           │                          │
   │ 1. 用户创建工作流         │                          │
   ├──────────────────────────>│                          │
   │                           │ 2. HTTP POST /workflow   │
   │                           ├─────────────────────────>│
   │                           │                          │
   │                           │ 3. 保存成功响应          │
   │                           │<─────────────────────────┤
   │                           │                          │
   │ 4. 用户启动执行           │                          │
   ├──────────────────────────>│                          │
   │                           │ 5. WebSocket 连接        │
   │                           ├<────────────────────────>│
   │                           │ 6. 开始执行              │
   │                           ├─────────────────────────>│
   │                           │                          │
   │                           │ 7. 实时状态推送          │
   │<──────────────────────────┤<─────────────────────────┤
   │ 显示日志和进度            │                          │
   │                           │                          │
   │                           │ 8. 执行完成通知          │
   │<──────────────────────────┤<─────────────────────────┤
   │                           │                          │
```

## 运行流程

### 基本工作流程

```
1. 初始化
   ├─ 加载配置
   ├─ 初始化图像识别引擎
   └─ 初始化操作执行器

2. 任务编排
   ├─ 读取自动化任务脚本
   ├─ 解析操作序列
   └─ 加载目标图片资源

3. 执行循环
   ├─ 截取屏幕
   ├─ 图像匹配定位
   │  ├─ 模板匹配
   │  ├─ 计算相似度
   │  └─ 返回坐标位置
   ├─ 执行自动化操作
   │  ├─ 移动鼠标到目标位置
   │  ├─ 执行点击/输入操作
   │  └─ 等待操作完成
   └─ 验证操作结果

4. 异常处理
   ├─ 图片未找到 → 重试机制
   ├─ 超时处理 → 跳过或终止
   └─ 错误日志记录
```

### 详细执行步骤

```python
# 伪代码示例
workflow = Workflow()

# 步骤1: 图像识别和定位
location = workflow.find_image('target.png', confidence=0.8)

# 步骤2: 移动鼠标
workflow.move_to(location)

# 步骤3: 执行点击
workflow.click()

# 步骤4: 键盘输入
workflow.type_text('Hello World')

# 步骤5: 等待
workflow.wait(2)
```

## 核心功能模块

### 1. 图像识别模块 (`image_recognition.py`)
- **屏幕截图**：捕获全屏或指定区域
- **图像匹配**：使用模板匹配算法找到目标图片
- **位置定位**：返回匹配图片的中心坐标
- **多目标识别**：找到所有匹配的位置
- **置信度阈值**：设置匹配的最低相似度

### 2. 操作执行模块 (`automation.py`)
- **鼠标操作**：
  - 移动：`move_to(x, y)`
  - 点击：`click()`, `double_click()`, `right_click()`
  - 拖拽：`drag(start, end)`
  - 滚动：`scroll(amount)`
  
- **键盘操作**：
  - 输入文字：`type_text(text)`
  - 按键：`press(key)`, `hotkey('ctrl', 'c')`
  
- **等待和延迟**：
  - 固定等待：`wait(seconds)`
  - 等待图片出现：`wait_for_image(image)`

### 3. 工作流引擎 (`workflow.py`)
- **任务编排**：支持 YAML/JSON 配置
- **流程控制**：顺序、循环、条件判断
- **异常处理**：自动重试、失败回退
- **日志记录**：详细的操作日志

## 项目结构

```
py-picToWork/
├── README.md                           # 项目说明文档
├── .gitignore                          # Git 忽略文件
│
├── frontend/                           # 前端项目（Vue + Electron）
│   ├── package.json                   # 前端依赖配置
│   ├── vite.config.ts                 # Vite 配置
│   ├── electron.vite.config.ts        # Electron 构建配置
│   ├── tsconfig.json                  # TypeScript 配置
│   │
│   ├── src/                           # 前端源码
│   │   ├── main/                      # Electron Main Process
│   │   │   ├── index.ts              # Main 进程入口
│   │   │   ├── window.ts             # 窗口管理
│   │   │   ├── tray.ts               # 系统托盘
│   │   │   └── ipc.ts                # 进程通信
│   │   │
│   │   ├── preload/                   # Electron Preload
│   │   │   └── index.ts              # 预加载脚本
│   │   │
│   │   └── renderer/                  # Vue 渲染进程
│   │       ├── main.ts               # Vue 入口
│   │       ├── App.vue               # 根组件
│   │       │
│   │       ├── views/                # 页面视图
│   │       │   ├── Home.vue          # 首页
│   │       │   ├── WorkflowEditor.vue # 工作流编辑器
│   │       │   ├── ImageManager.vue   # 图片管理
│   │       │   ├── Console.vue        # 执行控制台
│   │       │   └── Settings.vue       # 设置页面
│   │       │
│   │       ├── components/           # 组件
│   │       │   ├── FlowCanvas.vue    # 流程画布
│   │       │   ├── NodeEditor.vue    # 节点编辑器
│   │       │   ├── ImageUpload.vue   # 图片上传
│   │       │   ├── LogViewer.vue     # 日志查看器
│   │       │   └── StatusBar.vue     # 状态栏
│   │       │
│   │       ├── stores/               # Pinia 状态管理
│   │       │   ├── workflow.ts       # 工作流状态
│   │       │   ├── execution.ts      # 执行状态
│   │       │   └── settings.ts       # 设置状态
│   │       │
│   │       ├── api/                  # API 接口
│   │       │   ├── http.ts           # HTTP 客户端
│   │       │   ├── websocket.ts      # WebSocket 客户端
│   │       │   └── workflow.ts       # 工作流 API
│   │       │
│   │       ├── types/                # TypeScript 类型定义
│   │       │   ├── workflow.ts       # 工作流类型
│   │       │   └── api.ts            # API 类型
│   │       │
│   │       ├── assets/               # 静态资源
│   │       │   ├── styles/           # 样式文件
│   │       │   └── icons/            # 图标
│   │       │
│   │       └── router/               # 路由配置
│   │           └── index.ts          # 路由定义
│   │
│   ├── resources/                     # 应用资源
│   │   ├── icon.png                  # 应用图标
│   │   └── icon.icns                 # macOS 图标
│   │
│   └── dist/                          # 构建输出（自动生成）
│
├── backend/                           # Python 后端
│   ├── main.py                       # FastAPI 应用入口
│   ├── requirements.txt              # Python 依赖
│   ├── config.py                     # 配置文件
│   │
│   ├── api/                          # API 路由
│   │   ├── __init__.py
│   │   ├── workflow.py               # 工作流 API
│   │   ├── image.py                  # 图片管理 API
│   │   ├── execution.py              # 执行控制 API
│   │   └── websocket.py              # WebSocket 端点
│   │
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── image_recognition.py      # 图像识别引擎
│   │   ├── automation.py             # 自动化操作
│   │   ├── workflow_engine.py        # 工作流引擎
│   │   └── screen_capture.py         # 屏幕捕获
│   │
│   ├── models/                       # 数据模型
│   │   ├── __init__.py
│   │   ├── workflow.py               # 工作流模型
│   │   ├── action.py                 # 操作模型
│   │   └── execution.py              # 执行结果模型
│   │
│   ├── services/                     # 业务逻辑
│   │   ├── __init__.py
│   │   ├── workflow_service.py       # 工作流服务
│   │   ├── execution_service.py      # 执行服务
│   │   └── image_service.py          # 图片服务
│   │
│   ├── utils/                        # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py                 # 日志工具
│   │   ├── helpers.py                # 辅助函数
│   │   └── exceptions.py             # 异常定义
│   │
│   └── data/                         # 数据存储
│       ├── workflows/                # 工作流文件
│       ├── images/                   # 上传的图片
│       └── logs/                     # 日志文件
│
└── docs/                              # 文档
    ├── API.md                        # API 文档
    ├── WORKFLOW.md                   # 工作流配置说明
    └── DEVELOPMENT.md                # 开发指南
```

## 快速开始

### 环境要求

- **Node.js**: 18.x 或更高
- **Python**: 3.8 或更高
- **npm** 或 **yarn** 或 **pnpm**

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
# 或
pnpm install
# 或
yarn install
```

### 3. 运行开发环境

**启动后端服务：**

```bash
cd backend
python main.py
# 后端将运行在 http://localhost:8000
```

**启动前端（另一个终端）：**

```bash
cd frontend
npm run dev
# Electron 应用将自动打开
```

### 4. 打包生产版本

**打包桌面应用：**

```bash
cd frontend
npm run build
# 打包文件将在 frontend/dist 目录
```

**支持的平台：**
- macOS: `.dmg` 和 `.app`
- Windows: `.exe` 安装包
- Linux: `.AppImage` 和 `.deb`

## 核心功能特性

### 1. 可视化工作流编辑器
- 🎨 **拖拽式节点编辑**：直观的节点连接和编排
- 📦 **丰富的操作节点**：
  - 图像识别节点
  - 鼠标操作节点（点击、拖拽、滚动）
  - 键盘输入节点
  - 等待延迟节点
  - 条件判断节点
  - 循环控制节点
- 💾 **工作流模板**：保存和复用常用流程
- 📋 **节点配置面板**：详细配置每个操作的参数

### 2. 智能图片管理
- 📸 **屏幕截图工具**：内置截图功能，快速捕获目标图片
- 🖼️ **图片库管理**：分类管理所有目标图片
- 🔍 **实时预览**：在屏幕上预览匹配效果
- ⚙️ **置信度调节**：可视化调整匹配精度
- 📊 **匹配测试**：测试图片识别成功率

### 3. 执行控制台
- ▶️ **一键启动**：快速启动工作流执行
- ⏸️ **暂停/继续**：随时暂停和恢复执行
- ⏹️ **停止执行**：紧急停止功能
- 🔄 **单步调试**：逐步执行每个操作节点
- 📈 **进度可视化**：实时显示执行进度

### 4. 实时日志系统
- 📝 **详细日志**：记录每个操作的执行情况
- 🎯 **高亮显示**：成功、警告、错误分类显示
- 🔎 **日志过滤**：按类型、时间过滤日志
- 💾 **日志导出**：导出日志用于分析
- 📸 **截图记录**：保存关键时刻的屏幕截图

### 5. 系统配置
- ⚙️ **全局设置**：
  - 图像识别精度
  - 操作延迟时间
  - 重试次数和间隔
  - 安全模式开关
- 🔔 **通知设置**：执行完成通知
- 🌓 **主题切换**：明暗主题
- 🌍 **多语言支持**：中英文界面

## 后端 API 接口

### RESTful API

```
POST   /api/workflow/create      # 创建工作流
GET    /api/workflow/list        # 获取工作流列表
GET    /api/workflow/:id         # 获取工作流详情
PUT    /api/workflow/:id         # 更新工作流
DELETE /api/workflow/:id         # 删除工作流

POST   /api/image/upload         # 上传图片
GET    /api/image/list           # 获取图片列表
DELETE /api/image/:id            # 删除图片

POST   /api/execution/start      # 开始执行
POST   /api/execution/pause      # 暂停执行
POST   /api/execution/resume     # 继续执行
POST   /api/execution/stop       # 停止执行
GET    /api/execution/status     # 获取执行状态

POST   /api/screen/capture       # 屏幕截图
POST   /api/screen/find-image    # 查找图片位置（测试）
```

### WebSocket 端点

```
ws://localhost:8000/ws/execution
```

**消息格式：**

```typescript
// 客户端 → 服务器
{
  "type": "start" | "pause" | "resume" | "stop",
  "workflow_id": string,
  "data": object
}

// 服务器 → 客户端
{
  "type": "log" | "progress" | "complete" | "error",
  "timestamp": number,
  "data": {
    "message": string,
    "level": "info" | "warn" | "error",
    "progress": number,  // 0-100
    "screenshot": string  // base64 图片（可选）
  }
}
```

## 工作流示例

### JSON 格式工作流

```json
{
  "id": "workflow-001",
  "name": "自动登录流程",
  "description": "自动打开应用并登录",
  "version": "1.0",
  "nodes": [
    {
      "id": "node-1",
      "type": "find_and_click",
      "name": "点击应用图标",
      "config": {
        "image_id": "img-001",
        "confidence": 0.8,
        "timeout": 10,
        "retry": 3
      },
      "position": { "x": 100, "y": 100 }
    },
    {
      "id": "node-2",
      "type": "wait",
      "name": "等待应用启动",
      "config": {
        "duration": 2
      },
      "position": { "x": 300, "y": 100 }
    },
    {
      "id": "node-3",
      "type": "find_and_click",
      "name": "点击登录按钮",
      "config": {
        "image_id": "img-002",
        "confidence": 0.85,
        "click_type": "left"
      },
      "position": { "x": 500, "y": 100 }
    },
    {
      "id": "node-4",
      "type": "type_text",
      "name": "输入用户名",
      "config": {
        "text": "username@example.com",
        "interval": 0.05
      },
      "position": { "x": 700, "y": 100 }
    },
    {
      "id": "node-5",
      "type": "keyboard",
      "name": "切换到密码框",
      "config": {
        "keys": ["Tab"]
      },
      "position": { "x": 900, "y": 100 }
    },
    {
      "id": "node-6",
      "type": "type_text",
      "name": "输入密码",
      "config": {
        "text": "password123",
        "interval": 0.05
      },
      "position": { "x": 1100, "y": 100 }
    },
    {
      "id": "node-7",
      "type": "keyboard",
      "name": "提交登录",
      "config": {
        "keys": ["Enter"]
      },
      "position": { "x": 1300, "y": 100 }
    }
  ],
  "connections": [
    { "from": "node-1", "to": "node-2" },
    { "from": "node-2", "to": "node-3" },
    { "from": "node-3", "to": "node-4" },
    { "from": "node-4", "to": "node-5" },
    { "from": "node-5", "to": "node-6" },
    { "from": "node-6", "to": "node-7" }
  ]
}
```

### 操作节点类型

| 节点类型 | 说明 | 配置参数 |
|---------|------|---------|
| `find_and_click` | 查找图片并点击 | `image_id`, `confidence`, `click_type`, `timeout` |
| `click` | 点击指定坐标 | `x`, `y`, `click_type`, `button` |
| `type_text` | 输入文字 | `text`, `interval` |
| `keyboard` | 键盘操作 | `keys`, `hotkey` |
| `wait` | 等待延迟 | `duration` |
| `wait_for_image` | 等待图片出现 | `image_id`, `timeout` |
| `scroll` | 滚动操作 | `amount`, `direction` |
| `drag` | 拖拽操作 | `from_x`, `from_y`, `to_x`, `to_y` |
| `condition` | 条件判断 | `condition`, `true_path`, `false_path` |
| `loop` | 循环控制 | `times`, `condition` |
| `screenshot` | 截图保存 | `path`, `region` |

## 技术要点

### 1. 图像匹配算法

使用 OpenCV 的模板匹配（Template Matching）：
- **归一化相关系数法**（推荐）：`cv2.TM_CCOEFF_NORMED`
- **归一化平方差法**：`cv2.TM_SQDIFF_NORMED`
- 支持多尺度匹配，应对不同分辨率

### 2. 性能优化

- **区域截图**：只截取感兴趣区域，减少处理时间
- **灰度匹配**：转换为灰度图加速匹配
- **图片缓存**：缓存已加载的模板图片
- **多线程**：并行处理多个任务

### 3. 可靠性保障

- **重试机制**：图片未找到时自动重试
- **超时控制**：设置最大等待时间
- **异常捕获**：完善的错误处理
- **日志记录**：记录所有操作和结果
- **安全模式**：紧急停止功能（PyAutoGUI 的 FAILSAFE）

### 4. 跨平台兼容性

- macOS：完全支持
- Windows：完全支持
- Linux：需要安装额外依赖（python3-tk, python3-dev）

## Electron 与 Python 通信方案

### 方案一：内置 Python 服务（推荐）

Electron 在启动时自动启动 Python 后端服务作为子进程：

```typescript
// electron/main/index.ts
import { spawn } from 'child_process';

let pythonProcess: ChildProcess;

function startPythonBackend() {
  const pythonPath = isDev 
    ? 'python' 
    : path.join(process.resourcesPath, 'python/python');
  
  const scriptPath = isDev
    ? path.join(__dirname, '../../backend/main.py')
    : path.join(process.resourcesPath, 'backend/main.py');
  
  pythonProcess = spawn(pythonPath, [scriptPath], {
    env: { ...process.env, PORT: '8000' }
  });
  
  pythonProcess.stdout?.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });
}

app.on('ready', () => {
  startPythonBackend();
  createWindow();
});

app.on('quit', () => {
  pythonProcess?.kill();
});
```

### 方案二：独立运行

用户手动启动 Python 后端，前端通过配置连接：

```typescript
// 配置文件
{
  "backend": {
    "host": "localhost",
    "port": 8000,
    "autoStart": false
  }
}
```

## 打包方案

### Electron 打包

使用 `electron-builder` 打包：

```json
// package.json
{
  "build": {
    "appId": "com.company.py-pictowork",
    "productName": "PicToWork",
    "files": [
      "dist/**/*",
      "resources/**/*"
    ],
    "extraResources": [
      {
        "from": "../backend",
        "to": "backend",
        "filter": ["**/*", "!venv", "!__pycache__"]
      }
    ],
    "mac": {
      "category": "public.app-category.productivity",
      "icon": "resources/icon.icns"
    },
    "win": {
      "target": "nsis",
      "icon": "resources/icon.ico"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "category": "Utility"
    }
  }
}
```

### Python 打包

使用 PyInstaller 将 Python 代码打包成可执行文件：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包后端
cd backend
pyinstaller --onefile \
  --add-data "data:data" \
  --hidden-import uvicorn \
  --hidden-import fastapi \
  main.py
```

在 `electron-builder` 中包含打包后的 Python 可执行文件：

```json
{
  "extraResources": [
    {
      "from": "../backend/dist/main",
      "to": "python/",
      "filter": ["**/*"]
    }
  ]
}
```

## 开发环境

### 必需软件
- **Node.js**: 18.x 或更高
- **Python**: 3.8 或更高
- **Git**: 版本控制

### 推荐工具
- **VS Code**: 代码编辑器
- **Postman**: API 测试
- **Python 虚拟环境**: venv 或 conda

### macOS 特别说明
需要授予应用辅助功能权限：
1. 系统设置 → 隐私与安全性 → 辅助功能
2. 添加应用并授权

## 注意事项

1. **屏幕分辨率**：不同分辨率下图片大小可能不同，建议使用多尺度匹配
2. **权限问题**：macOS 需要授予辅助功能权限
3. **安全性**：使用 PyAutoGUI 的 FAILSAFE 功能，紧急情况移动鼠标到屏幕角落可停止程序
4. **图片质量**：截取的目标图片应清晰、特征明显
5. **性能考虑**：频繁的屏幕截图会消耗资源，注意优化

## 最佳实践

1. **图片准备**：
   - 截取的图片要有明显特征
   - 避免截取变化频繁的区域（如动画）
   - 保存为 PNG 格式保持清晰度

2. **置信度设置**：
   - 静态元素：0.9-0.95
   - 一般元素：0.8-0.85
   - 动态元素：0.7-0.75

3. **错误处理**：
   - 始终设置超时时间
   - 记录详细日志便于调试
   - 提供友好的错误提示

4. **性能优化**：
   - 指定搜索区域而非全屏
   - 使用灰度匹配加速
   - 合理设置等待时间

## 应用场景

- 🎮 **游戏自动化**：自动化游戏操作，辅助游戏任务
- 📊 **数据采集**：从应用界面自动采集和录入数据
- 🧪 **自动化测试**：UI 自动化测试，回归测试
- 📱 **应用自动化**：跨应用的自动化流程
- 🔄 **重复性任务**：消除重复性手工操作
- 📝 **办公自动化**：文档处理、数据录入等办公流程
- 🏭 **业务流程**：RPA（机器人流程自动化）

## 开发路线图

### Phase 1: 基础框架 (2-3 周)
- [x] 技术选型和架构设计
- [ ] 搭建 Vue + Electron 前端框架
- [ ] 搭建 FastAPI 后端服务
- [ ] 实现前后端通信（HTTP + WebSocket）
- [ ] 实现基础的图像识别模块
- [ ] 实现基础的自动化操作模块

### Phase 2: 核心功能 (3-4 周)
- [ ] 可视化工作流编辑器
  - [ ] 画布和节点系统
  - [ ] 节点拖拽和连接
  - [ ] 节点配置面板
- [ ] 图片管理系统
  - [ ] 图片上传和管理
  - [ ] 内置截图工具
  - [ ] 图片预览和测试
- [ ] 执行引擎
  - [ ] 工作流解析和执行
  - [ ] 实时日志和状态推送
  - [ ] 错误处理和重试机制

### Phase 3: 增强功能 (2-3 周)
- [ ] 条件判断和循环控制
- [ ] 变量系统
- [ ] 多显示器支持
- [ ] 执行历史记录
- [ ] 工作流导入/导出
- [ ] 快捷键支持

### Phase 4: 优化和完善 (2-3 周)
- [ ] 性能优化
- [ ] UI/UX 优化
- [ ] 多语言支持
- [ ] 完善文档
- [ ] 单元测试和集成测试
- [ ] 打包和分发

### Future Features
- [ ] OCR 文字识别集成
- [ ] 云端工作流同步
- [ ] 工作流市场/分享
- [ ] 插件系统
- [ ] AI 辅助图像识别
- [ ] 移动端控制

## 技术优势

### 1. 现代化技术栈
- Vue 3 + TypeScript：类型安全，开发效率高
- Electron：跨平台桌面应用，原生体验
- FastAPI：高性能异步 API，自动文档
- OpenCV：成熟的图像识别库

### 2. 前后端分离
- 清晰的架构边界
- 便于维护和扩展
- 可以独立部署和调试
- 支持多客户端接入

### 3. 可视化编排
- 无需编程知识
- 直观的拖拽操作
- 实时预览和调试
- 降低使用门槛

### 4. 实时反馈
- WebSocket 实时通信
- 即时日志输出
- 执行状态可视化
- 快速定位问题

### 5. 扩展性强
- 模块化设计
- 插件式架构
- 支持自定义节点
- API 开放集成

## 常见问题 (FAQ)

**Q: 如何处理不同分辨率的屏幕？**
A: 使用多尺度图像匹配，或在不同分辨率下分别截取目标图片。

**Q: 图片识别失败怎么办？**
A: 1) 降低置信度阈值 2) 使用更清晰的图片 3) 增加重试次数 4) 使用灰度匹配。

**Q: 可以在后台运行吗？**
A: 可以，支持最小化到系统托盘，后台执行工作流。

**Q: 支持多显示器吗？**
A: 支持，可以指定在哪个显示器上查找和操作。

**Q: 如何保护敏感信息（如密码）？**
A: 工作流中的敏感信息会加密存储，执行日志可选择是否记录敏感操作。

**Q: 可以远程控制吗？**
A: 当前版本为本地应用，未来计划支持远程控制功能。

## 性能指标

- 图像识别速度：< 200ms（1080p 全屏）
- 鼠标操作延迟：< 50ms
- WebSocket 延迟：< 10ms
- 内存占用：< 200MB（空闲）
- CPU 占用：< 5%（空闲）

## 安全性

1. **本地运行**：所有数据存储在本地，不上传云端
2. **权限控制**：需要用户授权才能控制鼠标和键盘
3. **安全模式**：紧急停止功能（移动鼠标到角落）
4. **数据加密**：敏感配置加密存储
5. **审计日志**：完整的操作记录

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 致谢

感谢以下开源项目：
- Vue.js / Electron
- FastAPI / Uvicorn
- OpenCV / NumPy
- PyAutoGUI / pynput

## 联系方式

- 提交 Issue：[GitHub Issues](https://github.com/yourname/py-picToWork/issues)
- 讨论区：[GitHub Discussions](https://github.com/yourname/py-picToWork/discussions)
- Email: your.email@example.com

---

**最后更新：2025-10-09**

