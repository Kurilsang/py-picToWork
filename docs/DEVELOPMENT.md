# 开发指南

## 快速开始

### 克隆项目

```bash
git clone https://github.com/yourname/py-picToWork.git
cd py-picToWork
```

### 后端开发

1. 创建虚拟环境并安装依赖：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 运行开发服务器：
```bash
python main.py
# 或使用热重载
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. 访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端开发

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 运行开发环境：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 代码规范

### Python 后端

- 使用 Black 格式化代码
- 使用 Flake8 检查代码质量
- 使用 Type Hints

```bash
# 格式化代码
black backend/

# 检查代码
flake8 backend/
```

### TypeScript 前端

- 使用 ESLint + Prettier
- 遵循 Vue 3 风格指南

```bash
# 格式化代码
npm run format

# 检查代码
npm run lint
```

## 项目结构详解

### 后端模块说明

- `api/`: API 路由定义
- `core/`: 核心业务逻辑（图像识别、自动化操作）
- `models/`: 数据模型定义
- `services/`: 业务服务层
- `utils/`: 工具函数

### 前端模块说明

- `main/`: Electron 主进程
- `renderer/`: Vue 渲染进程
  - `views/`: 页面组件
  - `components/`: 可复用组件
  - `stores/`: Pinia 状态管理
  - `api/`: API 接口封装

## 调试技巧

### 后端调试

使用 VS Code 的 Python 调试器：

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### 前端调试

1. Chrome DevTools：F12 打开开发者工具
2. Vue DevTools：安装 Vue.js devtools 扩展
3. Electron 调试：在主进程中使用 `console.log`

## 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```

## 常见问题

### 1. Python 后端启动失败

- 检查端口 8000 是否被占用
- 确认虚拟环境已激活
- 验证所有依赖已安装

### 2. Electron 无法连接后端

- 确认后端服务已启动
- 检查防火墙设置
- 验证端口配置正确

### 3. 图像识别不准确

- 调整置信度阈值
- 使用更清晰的目标图片
- 尝试灰度匹配模式

## 贡献流程

1. 在 Issues 中讨论新功能或 Bug
2. Fork 项目并创建分支
3. 编写代码和测试
4. 提交 Pull Request
5. 等待代码审查

## 发布流程

1. 更新版本号（package.json 和 backend/config.py）
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 构建和测试
5. 发布 Release

## 资源链接

- [Vue 3 文档](https://vuejs.org/)
- [Electron 文档](https://www.electronjs.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [OpenCV Python 教程](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
