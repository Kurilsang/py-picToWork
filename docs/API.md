# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **认证方式**: 暂无（本地应用）

## 工作流 API

### 创建工作流

```http
POST /api/workflow/create
Content-Type: application/json

{
  "name": "工作流名称",
  "description": "工作流描述",
  "nodes": [...],
  "connections": [...]
}
```

**响应**:
```json
{
  "id": "workflow-001",
  "name": "工作流名称",
  "created_at": "2025-10-09T12:00:00Z"
}
```

### 获取工作流列表

```http
GET /api/workflow/list
```

**响应**:
```json
{
  "workflows": [
    {
      "id": "workflow-001",
      "name": "工作流名称",
      "description": "工作流描述",
      "created_at": "2025-10-09T12:00:00Z",
      "updated_at": "2025-10-09T12:00:00Z"
    }
  ]
}
```

### 获取工作流详情

```http
GET /api/workflow/{workflow_id}
```

### 更新工作流

```http
PUT /api/workflow/{workflow_id}
Content-Type: application/json

{
  "name": "新名称",
  "nodes": [...],
  "connections": [...]
}
```

### 删除工作流

```http
DELETE /api/workflow/{workflow_id}
```

## 图片管理 API

### 上传图片

```http
POST /api/image/upload
Content-Type: multipart/form-data

file: <image file>
name: "按钮图标"
category: "ui_elements"
```

**响应**:
```json
{
  "id": "img-001",
  "name": "按钮图标",
  "path": "/data/images/img-001.png",
  "size": 12345,
  "created_at": "2025-10-09T12:00:00Z"
}
```

### 获取图片列表

```http
GET /api/image/list?category=ui_elements
```

### 删除图片

```http
DELETE /api/image/{image_id}
```

## 执行控制 API

### 开始执行

```http
POST /api/execution/start
Content-Type: application/json

{
  "workflow_id": "workflow-001",
  "options": {
    "debug_mode": false,
    "step_by_step": false
  }
}
```

**响应**:
```json
{
  "execution_id": "exec-001",
  "status": "running",
  "started_at": "2025-10-09T12:00:00Z"
}
```

### 暂停执行

```http
POST /api/execution/pause
Content-Type: application/json

{
  "execution_id": "exec-001"
}
```

### 继续执行

```http
POST /api/execution/resume
Content-Type: application/json

{
  "execution_id": "exec-001"
}
```

### 停止执行

```http
POST /api/execution/stop
Content-Type: application/json

{
  "execution_id": "exec-001"
}
```

### 获取执行状态

```http
GET /api/execution/status/{execution_id}
```

**响应**:
```json
{
  "execution_id": "exec-001",
  "workflow_id": "workflow-001",
  "status": "running",
  "progress": 45,
  "current_node": "node-3",
  "started_at": "2025-10-09T12:00:00Z",
  "logs": [...]
}
```

## 屏幕操作 API

### 屏幕截图

```http
POST /api/screen/capture
Content-Type: application/json

{
  "region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

**响应**:
```json
{
  "image": "base64_encoded_image",
  "timestamp": "2025-10-09T12:00:00Z"
}
```

### 查找图片位置（测试）

```http
POST /api/screen/find-image
Content-Type: application/json

{
  "image_id": "img-001",
  "confidence": 0.8
}
```

**响应**:
```json
{
  "found": true,
  "location": {
    "x": 500,
    "y": 300,
    "width": 100,
    "height": 50
  },
  "confidence": 0.92
}
```

## WebSocket API

### 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/execution');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### 消息格式

**客户端 → 服务器**:
```json
{
  "type": "start",
  "workflow_id": "workflow-001",
  "data": {}
}
```

**服务器 → 客户端**:

1. 日志消息
```json
{
  "type": "log",
  "timestamp": 1696857600,
  "data": {
    "level": "info",
    "message": "开始执行节点：点击按钮",
    "node_id": "node-1"
  }
}
```

2. 进度更新
```json
{
  "type": "progress",
  "timestamp": 1696857600,
  "data": {
    "progress": 50,
    "current_node": "node-3",
    "total_nodes": 6
  }
}
```

3. 完成通知
```json
{
  "type": "complete",
  "timestamp": 1696857600,
  "data": {
    "execution_id": "exec-001",
    "status": "success",
    "duration": 15.5
  }
}
```

4. 错误通知
```json
{
  "type": "error",
  "timestamp": 1696857600,
  "data": {
    "message": "图片未找到",
    "node_id": "node-2",
    "error_code": "IMAGE_NOT_FOUND"
  }
}
```

## 错误代码

| 代码 | 说明 |
|------|------|
| `WORKFLOW_NOT_FOUND` | 工作流不存在 |
| `IMAGE_NOT_FOUND` | 图片未找到 |
| `EXECUTION_FAILED` | 执行失败 |
| `INVALID_PARAMETERS` | 参数无效 |
| `TIMEOUT` | 操作超时 |
| `PERMISSION_DENIED` | 权限不足 |

## 速率限制

当前版本无速率限制（本地应用）。

## 注意事项

1. 所有时间戳使用 ISO 8601 格式
2. 所有文件路径使用相对路径
3. 图片使用 base64 编码传输
4. WebSocket 支持自动重连
