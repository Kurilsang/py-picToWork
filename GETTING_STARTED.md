# 项目启动指南

## 📋 已完成的工作

我已经为你的 py-picToWork 项目创建了完整的技术架构文档和示例文件。这是一个基于图像识别的屏幕自动化操作工具，采用前后端分离架构。

### 已创建的文件

```
py-picToWork/
├── README.md                        ✅ 完整的项目文档
├── .gitignore                       ✅ Git 忽略配置
├── main.py                          ✅ 项目说明启动文件
├── requirements.txt                 ✅ Python 依赖列表
├── backend-main.py.example          ✅ 后端服务示例代码
├── frontend-package.json.example    ✅ 前端配置示例
└── docs/                            ✅ 详细文档
    ├── API.md                       - API 接口文档
    ├── DEVELOPMENT.md               - 开发指南
    └── WORKFLOW.md                  - 工作流配置说明
```

## 🎯 技术架构概览

### 前端技术栈
- **Vue 3** - 现代化响应式前端框架
- **Electron** - 桌面应用打包，跨平台支持
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vite** - 快速构建工具

### 后端技术栈
- **FastAPI** - 高性能 Python Web 框架
- **OpenCV** - 图像识别核心引擎
- **pyautogui/pynput** - 系统操作控制
- **mss** - 高性能屏幕截图
- **WebSocket** - 实时双向通信

### 核心特性
1. 🎨 **可视化工作流编辑器** - 拖拽式节点编排
2. 🖼️ **智能图片管理** - 内置截图和图片库
3. ▶️ **执行控制台** - 实时监控和调试
4. 📝 **日志系统** - 详细的执行记录
5. ⚙️ **灵活配置** - 支持变量和条件判断

## 🚀 下一步行动

### 第一步：搭建后端服务

1. 创建后端目录结构：
```bash
mkdir -p backend/{api,core,models,services,utils,data/{workflows,images,logs}}
cd backend
touch api/__init__.py core/__init__.py models/__init__.py services/__init__.py utils/__init__.py
```

2. 复制示例文件：
```bash
cp ../backend-main.py.example main.py
```

3. 安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

4. 启动服务测试：
```bash
python main.py
# 访问 http://localhost:8000/docs 查看 API 文档
```

### 第二步：搭建前端项目

1. 使用 electron-vite 创建项目：
```bash
npm create @quick-start/electron@latest frontend
# 选择 Vue + TypeScript 模板
```

2. 进入前端目录并安装依赖：
```bash
cd frontend
npm install
```

3. 安装额外依赖：
```bash
npm install element-plus axios pinia vue-router
npm install -D sass
```

4. 启动开发服务器：
```bash
npm run dev
```

### 第三步：核心功能开发

按照以下优先级开发：

**Phase 1: 基础框架（2-3周）**
- [ ] 后端 FastAPI 基础框架
- [ ] 前端 Electron + Vue 基础框架
- [ ] HTTP/WebSocket 通信
- [ ] 基础图像识别模块
- [ ] 基础自动化操作模块

**Phase 2: 核心功能（3-4周）**
- [ ] 可视化工作流编辑器
- [ ] 图片管理系统
- [ ] 执行引擎和日志系统

**Phase 3: 增强功能（2-3周）**
- [ ] 条件判断和循环
- [ ] 变量系统
- [ ] 多显示器支持

**Phase 4: 优化完善（2-3周）**
- [ ] 性能优化
- [ ] UI/UX 改进
- [ ] 测试和文档

## 📚 重要文档

### 必读文档
1. **README.md** - 完整的项目说明、技术栈、架构设计
2. **docs/API.md** - 后端 API 接口规范
3. **docs/WORKFLOW.md** - 工作流配置和节点类型说明
4. **docs/DEVELOPMENT.md** - 开发规范和调试技巧

### 示例代码
- **backend-main.py.example** - FastAPI 后端服务完整示例
- **frontend-package.json.example** - Electron 打包配置示例

## 🔑 关键技术点

### 1. Electron 启动 Python 后端

在 Electron 主进程中：
```typescript
import { spawn } from 'child_process';

let pythonProcess = spawn('python', ['backend/main.py']);
pythonProcess.on('close', (code) => {
  console.log(`Backend exited with code ${code}`);
});
```

### 2. 前后端通信

- **HTTP REST API** - 用于 CRUD 操作
- **WebSocket** - 用于实时日志和状态推送

### 3. 图像识别

使用 OpenCV 的模板匹配：
```python
import cv2
import numpy as np

def find_image_on_screen(template_path, confidence=0.8):
    # 截取屏幕
    screenshot = capture_screen()
    # 加载模板
    template = cv2.imread(template_path)
    # 模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    # 找到最佳匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= confidence:
        return max_loc  # 返回坐标
    return None
```

### 4. 自动化操作

```python
import pyautogui

# 点击
pyautogui.click(x, y)

# 输入文字
pyautogui.write('Hello World', interval=0.05)

# 按键
pyautogui.press('enter')
pyautogui.hotkey('ctrl', 'c')
```

## ⚠️ 重要注意事项

### macOS 权限
需要授予辅助功能权限：
- 系统设置 → 隐私与安全性 → 辅助功能
- 添加 Terminal 和你的应用

### 安全模式
PyAutoGUI 默认开启 FAILSAFE，移动鼠标到屏幕角落可紧急停止。

### 图片质量
- 使用 PNG 格式保存目标图片
- 确保截图清晰，有明显特征
- 不同分辨率需要分别截图或使用多尺度匹配

## 🛠️ 推荐开发工具

- **VS Code** - 代码编辑器
  - 推荐插件：Volar, Python, ESLint, Prettier
- **Postman** - API 测试
- **Chrome DevTools** - 前端调试
- **Vue DevTools** - Vue 组件调试

## 📦 打包发布

### 开发环境打包测试
```bash
cd frontend
npm run pack
```

### 生产环境打包
```bash
# macOS
npm run dist:mac

# Windows
npm run dist:win

# Linux
npm run dist:linux
```

打包文件位于 `frontend/release/` 目录。

## 🤝 需要帮助？

1. 查看 **README.md** 中的常见问题 (FAQ)
2. 阅读 **docs/** 目录下的详细文档
3. 参考 **backend-main.py.example** 示例代码
4. 检查各个模块的注释和文档字符串

## 📈 项目规模估算

- **代码行数预估**: 10,000 - 15,000 行
  - 后端: 5,000 - 7,000 行
  - 前端: 5,000 - 8,000 行
  
- **开发时间预估**: 10-13 周（1人全职）
  - Phase 1: 2-3 周
  - Phase 2: 3-4 周
  - Phase 3: 2-3 周
  - Phase 4: 2-3 周

- **核心挑战**:
  1. 图像识别的准确性和性能优化
  2. 可视化工作流编辑器的实现
  3. Electron 和 Python 的进程管理
  4. 跨平台兼容性

## 🎉 开始开发

一切准备就绪！你现在可以：

1. ✅ 查看完整的 **README.md** 了解项目全貌
2. ✅ 按照上面的步骤创建 backend 和 frontend 目录
3. ✅ 开始编写核心功能代码
4. ✅ 参考示例文件和文档进行开发

祝你开发顺利！🚀

---

**文档创建时间**: 2025-10-09  
**技术架构**: Vue 3 + Electron + Python FastAPI + OpenCV
