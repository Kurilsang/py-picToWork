# 工作流配置说明

## 工作流结构

一个完整的工作流由以下部分组成：

```json
{
  "id": "唯一标识符",
  "name": "工作流名称",
  "description": "工作流描述",
  "version": "版本号",
  "nodes": [...],        // 节点数组
  "connections": [...],  // 连接关系
  "variables": {...}     // 变量定义（可选）
}
```

## 节点类型详解

### 1. find_and_click - 查找并点击

查找屏幕上的图片并点击。

```json
{
  "id": "node-1",
  "type": "find_and_click",
  "name": "点击登录按钮",
  "config": {
    "image_id": "img-001",           // 目标图片 ID（必需）
    "confidence": 0.8,                // 匹配置信度 0-1（默认 0.8）
    "timeout": 10,                    // 超时时间（秒，默认 10）
    "retry": 3,                       // 重试次数（默认 3）
    "click_type": "left",             // 点击类型：left/right/double（默认 left）
    "offset": { "x": 0, "y": 0 },    // 点击偏移（可选）
    "region": null                    // 搜索区域（可选）
  }
}
```

### 2. click - 点击坐标

点击指定坐标位置。

```json
{
  "id": "node-2",
  "type": "click",
  "name": "点击固定位置",
  "config": {
    "x": 500,                         // X 坐标（必需）
    "y": 300,                         // Y 坐标（必需）
    "click_type": "left",             // 点击类型（默认 left）
    "button": "left",                 // 鼠标按钮（默认 left）
    "clicks": 1                       // 点击次数（默认 1）
  }
}
```

### 3. type_text - 输入文字

在当前焦点位置输入文字。

```json
{
  "id": "node-3",
  "type": "type_text",
  "name": "输入用户名",
  "config": {
    "text": "username@example.com",   // 要输入的文字（必需）
    "interval": 0.05,                 // 字符间隔（秒，默认 0.05）
    "press_enter": false              // 是否在结尾按回车（默认 false）
  }
}
```

### 4. keyboard - 键盘操作

执行键盘按键或组合键。

```json
{
  "id": "node-4",
  "type": "keyboard",
  "name": "复制文本",
  "config": {
    "keys": ["Ctrl", "c"],            // 按键数组（必需）
    "press_type": "hotkey"            // 按键类型：hotkey/sequence（默认 hotkey）
  }
}
```

常用按键：
- 修饰键：`Ctrl`, `Alt`, `Shift`, `Cmd` (macOS)
- 功能键：`F1`-`F12`, `Enter`, `Tab`, `Backspace`, `Delete`, `Escape`
- 方向键：`Up`, `Down`, `Left`, `Right`
- 其他：`Space`, `Home`, `End`, `PageUp`, `PageDown`

### 5. wait - 等待延迟

等待指定时间。

```json
{
  "id": "node-5",
  "type": "wait",
  "name": "等待加载",
  "config": {
    "duration": 2.5                   // 等待时间（秒，必需）
  }
}
```

### 6. wait_for_image - 等待图片出现

等待图片在屏幕上出现。

```json
{
  "id": "node-6",
  "type": "wait_for_image",
  "name": "等待加载完成",
  "config": {
    "image_id": "img-002",            // 目标图片 ID（必需）
    "timeout": 30,                    // 超时时间（秒，默认 30）
    "confidence": 0.8,                // 匹配置信度（默认 0.8）
    "check_interval": 0.5             // 检查间隔（秒，默认 0.5）
  }
}
```

### 7. scroll - 滚动操作

滚动鼠标滚轮。

```json
{
  "id": "node-7",
  "type": "scroll",
  "name": "向下滚动",
  "config": {
    "amount": -3,                     // 滚动量（负数向下，正数向上）
    "x": null,                        // 滚动位置 X（可选）
    "y": null                         // 滚动位置 Y（可选）
  }
}
```

### 8. drag - 拖拽操作

拖拽鼠标从一个位置到另一个位置。

```json
{
  "id": "node-8",
  "type": "drag",
  "name": "拖拽元素",
  "config": {
    "from_x": 100,                    // 起始 X 坐标（必需）
    "from_y": 200,                    // 起始 Y 坐标（必需）
    "to_x": 500,                      // 目标 X 坐标（必需）
    "to_y": 300,                      // 目标 Y 坐标（必需）
    "duration": 0.5,                  // 拖拽持续时间（秒，默认 0.5）
    "button": "left"                  // 鼠标按钮（默认 left）
  }
}
```

### 9. condition - 条件判断

根据条件选择执行路径。

```json
{
  "id": "node-9",
  "type": "condition",
  "name": "检查图片是否存在",
  "config": {
    "condition_type": "image_exists",  // 条件类型（必需）
    "image_id": "img-003",             // 用于条件判断的图片
    "confidence": 0.8,
    "true_path": "node-10",            // 条件为真时的下一个节点
    "false_path": "node-11"            // 条件为假时的下一个节点
  }
}
```

条件类型：
- `image_exists`: 图片是否存在
- `variable_equals`: 变量值是否相等
- `custom`: 自定义条件表达式

### 10. loop - 循环控制

重复执行一组操作。

```json
{
  "id": "node-10",
  "type": "loop",
  "name": "重复 5 次",
  "config": {
    "loop_type": "count",             // 循环类型：count/while（必需）
    "times": 5,                       // 循环次数（count 类型必需）
    "condition": null,                // 循环条件（while 类型必需）
    "body_start": "node-11",          // 循环体起始节点
    "body_end": "node-15",            // 循环体结束节点
    "max_iterations": 100             // 最大迭代次数（防止死循环）
  }
}
```

### 11. screenshot - 截图保存

截取屏幕并保存。

```json
{
  "id": "node-11",
  "type": "screenshot",
  "name": "保存截图",
  "config": {
    "path": "screenshots/result.png", // 保存路径（必需）
    "region": null,                   // 截图区域（可选）
    "format": "png"                   // 图片格式：png/jpg（默认 png）
  }
}
```

## 连接关系

连接定义了节点之间的执行顺序。

```json
{
  "connections": [
    {
      "from": "node-1",                // 源节点 ID
      "to": "node-2",                  // 目标节点 ID
      "condition": null                // 条件（可选）
    },
    {
      "from": "node-2",
      "to": "node-3"
    }
  ]
}
```

## 变量系统

工作流支持变量定义和使用。

### 定义变量

```json
{
  "variables": {
    "username": {
      "type": "string",
      "value": "admin",
      "description": "用户名"
    },
    "retry_count": {
      "type": "number",
      "value": 3,
      "description": "重试次数"
    }
  }
}
```

### 使用变量

在节点配置中使用 `${variable_name}` 引用变量：

```json
{
  "type": "type_text",
  "config": {
    "text": "${username}"
  }
}
```

## 完整示例

### 示例 1：自动登录

```json
{
  "id": "login-workflow",
  "name": "自动登录流程",
  "description": "打开应用并自动登录",
  "version": "1.0",
  "variables": {
    "username": {
      "type": "string",
      "value": "user@example.com"
    },
    "password": {
      "type": "string",
      "value": "password123"
    }
  },
  "nodes": [
    {
      "id": "node-1",
      "type": "find_and_click",
      "name": "点击应用图标",
      "config": {
        "image_id": "app-icon",
        "confidence": 0.8
      }
    },
    {
      "id": "node-2",
      "type": "wait",
      "name": "等待应用启动",
      "config": {
        "duration": 3
      }
    },
    {
      "id": "node-3",
      "type": "find_and_click",
      "name": "点击登录按钮",
      "config": {
        "image_id": "login-button",
        "confidence": 0.85
      }
    },
    {
      "id": "node-4",
      "type": "type_text",
      "name": "输入用户名",
      "config": {
        "text": "${username}"
      }
    },
    {
      "id": "node-5",
      "type": "keyboard",
      "name": "切换到密码框",
      "config": {
        "keys": ["Tab"]
      }
    },
    {
      "id": "node-6",
      "type": "type_text",
      "name": "输入密码",
      "config": {
        "text": "${password}"
      }
    },
    {
      "id": "node-7",
      "type": "keyboard",
      "name": "提交登录",
      "config": {
        "keys": ["Enter"]
      }
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

### 示例 2：带条件判断的工作流

```json
{
  "id": "conditional-workflow",
  "name": "条件判断示例",
  "description": "根据界面状态执行不同操作",
  "nodes": [
    {
      "id": "node-1",
      "type": "condition",
      "name": "检查是否已登录",
      "config": {
        "condition_type": "image_exists",
        "image_id": "logout-button",
        "confidence": 0.8,
        "true_path": "node-2",
        "false_path": "node-3"
      }
    },
    {
      "id": "node-2",
      "type": "find_and_click",
      "name": "点击注销",
      "config": {
        "image_id": "logout-button"
      }
    },
    {
      "id": "node-3",
      "type": "find_and_click",
      "name": "点击登录",
      "config": {
        "image_id": "login-button"
      }
    }
  ],
  "connections": [
    { "from": "node-2", "to": "node-3" }
  ]
}
```

## 最佳实践

1. **合理设置超时时间**：根据实际应用响应速度设置
2. **使用适当的置信度**：静态元素用高置信度，动态元素用低置信度
3. **添加等待延迟**：在关键操作后添加等待，确保界面加载完成
4. **使用变量**：避免硬编码，提高工作流复用性
5. **错误处理**：使用条件判断处理可能的错误情况
6. **节点命名**：使用有意义的名称，便于理解和维护
7. **模块化设计**：将复杂工作流拆分为多个小工作流

## 调试技巧

1. **单步执行**：使用调试模式逐步执行每个节点
2. **截图记录**：在关键步骤添加截图节点
3. **日志输出**：查看执行日志了解每步的执行情况
4. **测试图片匹配**：使用图片测试功能验证识别效果
5. **逐步调整**：从简单工作流开始，逐步增加复杂度
