# 🖥️ 多显示器调试指南

## 问题：坐标超出屏幕范围

### 错误信息
```
❌ 执行失败
{ "success": false, "error": "Coordinates out of screen bounds" }
```

## ✅ 已修复

我已经修复了坐标验证逻辑：
- ✅ 现在检查所有显示器的范围
- ✅ 显示每个显示器的坐标范围
- ✅ 即使坐标看起来超出范围，也会尝试点击

## 🔍 调试步骤

### 1. 重启服务

**重要**：必须重启服务才能应用修复！

```bash
# 按 Ctrl+C 停止当前服务

# 重新启动
cd /Users/ann/Desktop/gitlab/fish/py-picToWork/backend
source venv/bin/activate
python main.py
```

### 2. 查看显示器信息

访问 API 端点查看系统检测到的显示器：

```bash
curl http://localhost:8899/api/monitors
```

**预期输出**：
```json
{
  "success": true,
  "count": 2,
  "monitors": [
    {
      "id": 1,
      "name": "显示器 1",
      "width": 1920,
      "height": 1080,
      "left": 0,
      "top": 0
    },
    {
      "id": 2,
      "name": "显示器 2",
      "width": 2560,
      "height": 1440,
      "left": 1920,
      "top": 0
    }
  ]
}
```

### 3. 查看执行日志

重新上传图片并执行，现在会看到详细信息：

```
🖥️ 检测到 2 个显示器: 显示器1(1920x1080), 显示器2(2560x1440)
🔍 开始识别屏幕 (置信度: 0.8)
✅ 找到目标图片！匹配度: 92% (显示器 2)
🔍 坐标详情: 绝对(2500, 500), 相对(580, 500), 显示器偏移(1920, 0)
📺 显示器范围: 显示器1[0,0-1920,1080], 显示器2[1920,0-4480,1440]
✅ 坐标在显示器2范围内
🖱️ 准备点击坐标: (2500, 500)
✅ 点击成功！
```

## 🐛 常见问题

### 问题1：显示器数量不对

**症状**：只检测到1个显示器，但实际有2个

**原因**：
- 扩展屏未正确配置
- 镜像模式而非扩展模式

**解决**：
```
macOS: 系统设置 → 显示器 → 排列
确保：
- 未勾选"镜像显示器"
- 显示器图标分开排列
```

### 问题2：坐标仍然超出范围

**可能原因A：显示器偏移计算错误**

检查日志中的显示器范围：
```
📺 显示器范围: 显示器1[0,0-1920,1080], 显示器2[1920,0-4480,1440]
```

如果坐标是 `(2500, 500)`，应该在显示器2的范围内：
- X: 1920 ≤ 2500 ≤ 4480 ✅
- Y: 0 ≤ 500 ≤ 1440 ✅

**可能原因B：macOS 坐标系统问题**

macOS 的坐标系统可能与其他系统不同。检查：

```python
# 在 Python 中测试
import pyautogui
import mss

# 获取 PyAutoGUI 看到的屏幕大小
print("PyAutoGUI screen size:", pyautogui.size())

# 获取 MSS 看到的所有显示器
with mss.mss() as sct:
    for i, monitor in enumerate(sct.monitors):
        print(f"Monitor {i}:", monitor)
```

### 问题3：找到图片但点击失败

**症状**：日志显示找到图片，但点击没反应

**原因**：
- 辅助功能权限不足
- PyAutoGUI 在多显示器环境下的限制

**解决方案A：检查权限**
```
系统设置 → 隐私与安全性 → 辅助功能
确保勾选：
- ✅ 终端
- ✅ Python（如果有）
```

**解决方案B：使用相对坐标**

如果绝对坐标有问题，可以尝试使用显示器内的相对坐标。

修改 `backend/main.py`：
```python
# 尝试使用相对坐标
local_x = location.get('local_x')
local_y = location.get('local_y')
monitor_id = location.get('monitor_id')

# 如果是第二个显示器，可能需要特殊处理
if monitor_id > 1:
    # 方案1：使用绝对坐标（当前方式）
    pyautogui.moveTo(x, y)
    
    # 方案2：先移动到显示器起点，再移动相对坐标
    # monitor = get_all_monitors()[monitor_id - 1]
    # pyautogui.moveTo(monitor['left'] + local_x, monitor['top'] + local_y)
```

## 🔧 临时解决方案

如果多显示器仍有问题，可以临时只在主显示器上工作：

### 方案1：移动窗口到主显示器

将目标应用窗口拖到主显示器（显示器1）。

### 方案2：指定搜索显示器

未来版本会支持选择特定显示器搜索。

### 方案3：禁用扩展屏测试

临时断开或禁用扩展屏，确认单显示器环境下是否正常。

## 📊 收集调试信息

如果问题持续，请提供以下信息：

### 1. 显示器配置

```bash
curl http://localhost:8899/api/monitors | python3 -m json.tool
```

### 2. 完整日志

上传图片并执行后，复制所有日志输出。

### 3. 系统信息

```bash
# macOS版本
sw_vers

# 屏幕分辨率
system_profiler SPDisplaysDataType | grep Resolution

# Python版本
python --version

# PyAutoGUI版本
pip show pyautogui | grep Version
```

### 4. 测试脚本输出

创建测试脚本 `test_coordinates.py`：

```python
import pyautogui
import mss

print("=== PyAutoGUI Info ===")
print(f"Screen size: {pyautogui.size()}")
print(f"Position: {pyautogui.position()}")

print("\n=== MSS Monitors ===")
with mss.mss() as sct:
    for i, monitor in enumerate(sct.monitors):
        print(f"Monitor {i}: {monitor}")

print("\n=== Test Movement ===")
try:
    current_pos = pyautogui.position()
    print(f"Current position: {current_pos}")
    
    # 测试移动到不同位置
    test_positions = [
        (100, 100),
        (1000, 500),
        (2000, 500) if pyautogui.size()[0] < 2000 else (1000, 500)
    ]
    
    for pos in test_positions:
        try:
            pyautogui.moveTo(pos[0], pos[1], duration=0.5)
            actual_pos = pyautogui.position()
            print(f"Moved to {pos}, actual: {actual_pos}")
        except Exception as e:
            print(f"Failed to move to {pos}: {e}")
    
    # 恢复原位置
    pyautogui.moveTo(current_pos[0], current_pos[1])
    
except Exception as e:
    print(f"Error: {e}")
```

运行：
```bash
cd /Users/ann/Desktop/gitlab/fish/py-picToWork/backend
source venv/bin/activate
python test_coordinates.py
```

## 🎯 预期行为

修复后的行为：

1. **检测显示器**
   ```
   🖥️ 检测到 2 个显示器: 显示器1(1920x1080), 显示器2(2560x1440)
   ```

2. **搜索所有显示器**
   ```
   📺 各显示器匹配度: 显示器1: 45%, 显示器2: 92%
   ```

3. **验证坐标**
   ```
   📺 显示器范围: 显示器1[0,0-1920,1080], 显示器2[1920,0-4480,1440]
   ✅ 坐标在显示器2范围内
   ```

4. **执行点击**
   ```
   🖱️ 准备点击坐标: (2500, 500)
   ✅ 点击成功！位置: (2500, 500)
   ```

## 📞 获取帮助

如果仍然有问题：

1. ✅ 确认已重启服务
2. ✅ 收集上述调试信息
3. ✅ 提供完整日志输出
4. ✅ 运行测试脚本

---

**更新时间**: 2025-10-10  
**版本**: v1.1.1  
**修复内容**: 多显示器坐标验证逻辑
