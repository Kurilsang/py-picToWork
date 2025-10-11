#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
py-picToWork 简化版后端
实现图片识别和自动点击功能
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
import pyautogui
import mss
from PIL import Image
from typing import List
import asyncio
import json
from datetime import datetime
import os
import platform

# 导入图像匹配模块
from image_matcher import find_image_on_screen_multi_monitor

# PyAutoGUI 安全配置
pyautogui.FAILSAFE = True  # 移动鼠标到角落可以紧急停止
pyautogui.PAUSE = 0.1  # 每次操作后暂停 0.1 秒

# macOS 特殊配置 - 防止意外的系统行为
if platform.system() == 'Darwin':  # macOS
    # 禁用 PyAutoGUI 的某些自动行为，避免触发系统功能
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)

# 创建 FastAPI 应用
app = FastAPI(title="py-picToWork MVP")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_log(websocket, "info", "WebSocket 连接成功")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_log(self, websocket: WebSocket, level: str, message: str, data: dict = None):
        """发送日志到前端"""
        log_data = {
            "type": "log",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
            "data": data or {}
        }
        try:
            await websocket.send_json(log_data)
        except:
            pass

manager = ConnectionManager()

def get_all_monitors():
    """获取所有显示器信息"""
    with mss.mss() as sct:
        monitors = []
        for i, monitor in enumerate(sct.monitors[1:], 1):  # 跳过第0个（全屏）
            monitors.append({
                "id": i,
                "left": monitor["left"],
                "top": monitor["top"],
                "width": monitor["width"],
                "height": monitor["height"],
                "name": f"显示器 {i}"
            })
        return monitors

def capture_screenshot(monitor_id=None):
    """
    截取屏幕
    monitor_id: None表示所有显示器，数字表示指定显示器
    返回: 图片或图片列表
    """
    with mss.mss() as sct:
        if monitor_id is None:
            # 截取所有显示器
            screenshots = []
            for i, monitor in enumerate(sct.monitors[1:], 1):
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                screenshots.append({
                    "monitor_id": i,
                    "image": img,
                    "offset_x": monitor["left"],
                    "offset_y": monitor["top"],
                    "width": monitor["width"],
                    "height": monitor["height"]
                })
            return screenshots
        else:
            # 截取指定显示器
            if monitor_id < 1 or monitor_id >= len(sct.monitors):
                monitor_id = 1  # 默认主显示器
            
            monitor = sct.monitors[monitor_id]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return [{
                "monitor_id": monitor_id,
                "image": img,
                "offset_x": monitor["left"],
                "offset_y": monitor["top"],
                "width": monitor["width"],
                "height": monitor["height"]
            }]

def find_image_on_screen(template_path, confidence=0.8, enable_debug=False, monitor_id=None):
    """
    图像识别包装函数 - 支持多尺度、多算法和多显示器匹配
    monitor_id: None=搜索所有显示器, 数字=指定显示器
    返回: (found, location, match_confidence, match_info)
    """
    # 截取屏幕（单个或所有显示器）
    screenshots = capture_screenshot(monitor_id)
    
    # 调用新的图像匹配模块
    return find_image_on_screen_multi_monitor(screenshots, template_path, confidence, enable_debug)

@app.get("/api/monitors")
async def get_monitors():
    """获取所有显示器信息"""
    try:
        monitors = get_all_monitors()
        return {
            "success": True,
            "monitors": monitors,
            "count": len(monitors)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>py-picToWork - 图像识别自动化工具</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
            .card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .card h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.5em;
            }
            
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 40px 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                margin-bottom: 20px;
            }
            
            .upload-area:hover {
                background: #f8f9ff;
                border-color: #764ba2;
            }
            
            .upload-area.dragover {
                background: #f0f0ff;
                border-color: #764ba2;
            }
            
            #fileInput {
                display: none;
            }
            
            .preview {
                margin: 20px 0;
                text-align: center;
            }
            
            .preview img {
                max-width: 100%;
                max-height: 200px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .controls {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            .btn {
                flex: 1;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .btn-primary:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-secondary:hover {
                background: #e0e0e0;
            }
            
            .settings {
                margin-top: 20px;
            }
            
            .setting-item {
                margin-bottom: 15px;
            }
            
            .setting-item label {
                display: block;
                margin-bottom: 5px;
                color: #666;
                font-size: 14px;
            }
            
            .setting-item input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .log-container {
                background: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
                max-height: 500px;
                overflow-y: auto;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 13px;
            }
            
            .log-entry {
                padding: 8px 12px;
                margin-bottom: 5px;
                border-radius: 4px;
                line-height: 1.5;
            }
            
            .log-entry.info {
                background: rgba(52, 152, 219, 0.1);
                color: #3498db;
            }
            
            .log-entry.success {
                background: rgba(46, 204, 113, 0.1);
                color: #2ecc71;
            }
            
            .log-entry.warning {
                background: rgba(241, 196, 15, 0.1);
                color: #f1c40f;
            }
            
            .log-entry.error {
                background: rgba(231, 76, 60, 0.1);
                color: #e74c3c;
            }
            
            .log-time {
                opacity: 0.7;
                margin-right: 10px;
            }
            
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .status-badge.connected {
                background: rgba(46, 204, 113, 0.2);
                color: #2ecc71;
            }
            
            .status-badge.disconnected {
                background: rgba(231, 76, 60, 0.2);
                color: #e74c3c;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 py-picToWork</h1>
                <p>基于图像识别的屏幕自动化操作工具</p>
            </div>
            
            <div class="main-content">
                <!-- 左侧：上传和控制 -->
                <div class="card">
                    <h2>📤 图片上传</h2>
                    
                    <div class="upload-area" id="uploadArea">
                        <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
                        <p style="color: #667eea; font-size: 16px; margin-bottom: 5px;">
                            点击或拖拽图片到这里
                        </p>
                        <p style="color: #999; font-size: 14px;">
                            支持 PNG, JPG 格式
                        </p>
                    </div>
                    
                    <input type="file" id="fileInput" accept="image/*">
                    
                    <div class="preview" id="preview" style="display: none;">
                        <img id="previewImage" src="" alt="预览">
                        <p style="margin-top: 10px; color: #666;" id="fileName"></p>
                    </div>
                    
                    <div class="settings">
                        <div class="setting-item">
                            <label>匹配置信度 (0.0 - 1.0)</label>
                            <input type="number" id="confidence" value="0.8" min="0" max="1" step="0.05">
                        </div>
                    </div>
                    
                    <div class="controls">
                        <button class="btn btn-primary" id="executeBtn" disabled>
                            🚀 识别并点击
                        </button>
                        <button class="btn btn-secondary" id="clearBtn">
                            🗑️ 清空
                        </button>
                    </div>
                </div>
                
                <!-- 右侧：日志输出 -->
                <div class="card">
                    <h2>📝 执行日志</h2>
                    <div id="wsStatus" class="status-badge disconnected">● 未连接</div>
                    <div class="log-container" id="logContainer">
                        <div class="log-entry info">
                            <span class="log-time">[系统]</span>
                            等待 WebSocket 连接...
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let selectedFile = null;
            let isConnected = false;
            
            // WebSocket 连接
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                ws.onopen = () => {
                    isConnected = true;
                    updateStatus(true);
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    addLog(data.level, data.message, data.data);
                };
                
                ws.onclose = () => {
                    isConnected = false;
                    updateStatus(false);
                    // 5秒后重连
                    setTimeout(connectWebSocket, 5000);
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            function updateStatus(connected) {
                const statusEl = document.getElementById('wsStatus');
                if (connected) {
                    statusEl.className = 'status-badge connected';
                    statusEl.textContent = '● 已连接';
                } else {
                    statusEl.className = 'status-badge disconnected';
                    statusEl.textContent = '● 未连接';
                }
            }
            
            function addLog(level, message, data) {
                const logContainer = document.getElementById('logContainer');
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry ${level}`;
                
                const now = new Date().toLocaleTimeString('zh-CN', { hour12: false });
                let logText = `<span class="log-time">[${now}]</span>${message}`;
                
                if (data && Object.keys(data).length > 0) {
                    logText += `<br><span style="opacity: 0.8; font-size: 12px;">${JSON.stringify(data, null, 2)}</span>`;
                }
                
                logEntry.innerHTML = logText;
                logContainer.appendChild(logEntry);
                
                // 自动滚动到底部
                logContainer.scrollTop = logContainer.scrollHeight;
            }
            
            // 文件上传相关
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const preview = document.getElementById('preview');
            const previewImage = document.getElementById('previewImage');
            const fileName = document.getElementById('fileName');
            const executeBtn = document.getElementById('executeBtn');
            const clearBtn = document.getElementById('clearBtn');
            
            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFile(files[0]);
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });
            
            function handleFile(file) {
                if (!file.type.startsWith('image/')) {
                    alert('请选择图片文件！');
                    return;
                }
                
                selectedFile = file;
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                    fileName.textContent = file.name;
                    preview.style.display = 'block';
                    executeBtn.disabled = false;
                };
                reader.readAsDataURL(file);
                
                addLog('info', `已选择图片: ${file.name}`, {});
            }
            
            clearBtn.addEventListener('click', () => {
                selectedFile = null;
                preview.style.display = 'none';
                fileInput.value = '';
                executeBtn.disabled = true;
                addLog('info', '已清空选择', {});
            });
            
            executeBtn.addEventListener('click', async () => {
                if (!selectedFile || !isConnected) {
                    return;
                }
                
                executeBtn.disabled = true;
                executeBtn.textContent = '⏳ 执行中...';
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('confidence', document.getElementById('confidence').value);
                
                try {
                    const response = await fetch('/api/execute', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        addLog('success', '✅ 执行成功', result);
                    } else {
                        addLog('error', '❌ 执行失败', result);
                    }
                } catch (error) {
                    addLog('error', `❌ 请求失败: ${error.message}`, {});
                } finally {
                    executeBtn.disabled = false;
                    executeBtn.textContent = '🚀 识别并点击';
                }
            });
            
            // 初始化
            connectWebSocket();
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 保持连接
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/execute")
async def execute_task(
    file: UploadFile = File(...),
    confidence: float = Form(0.8)
):
    """
    执行识别和点击任务
    """
    # 获取第一个连接的 WebSocket
    websocket = manager.active_connections[0] if manager.active_connections else None
    
    if not websocket:
        return {"success": False, "error": "No WebSocket connection"}
    
    try:
        # 保存上传的图片
        upload_dir = "backend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"target_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        await manager.send_log(websocket, "info", f"📁 图片已保存: {file.filename}")
        
        # 获取显示器信息
        monitors = get_all_monitors()
        monitor_summary = ", ".join([f"显示器{m['id']}({m['width']}x{m['height']})" for m in monitors])
        await manager.send_log(websocket, "info", f"🖥️ 检测到 {len(monitors)} 个显示器: {monitor_summary}")
        
        await manager.send_log(websocket, "info", f"🔍 开始识别屏幕 (置信度: {confidence})")
        await manager.send_log(websocket, "info", "🔬 使用多算法和多尺度匹配...")
        
        # 查找图片（启用调试模式）
        found, location, match_confidence, match_info = find_image_on_screen(file_path, confidence, enable_debug=True)
        
        # 输出详细的坐标信息用于调试
        if found and location:
            await manager.send_log(
                websocket,
                "info",
                f"🔍 坐标详情: 绝对({location.get('x')}, {location.get('y')}), "
                f"相对({location.get('local_x')}, {location.get('local_y')}), "
                f"显示器偏移({location.get('top_left', {}).get('x', 0) - location.get('local_x', 0) + location.get('width', 0)//2}, "
                f"{location.get('top_left', {}).get('y', 0) - location.get('local_y', 0) + location.get('height', 0)//2})"
            )
        
        # 显示匹配详情
        if match_info.get("methods_tried"):
            methods_text = ", ".join([
                f"{m['method']}: {m.get('confidence', 0):.2%}" 
                for m in match_info["methods_tried"] 
                if 'confidence' in m
            ])
            await manager.send_log(
                websocket,
                "info",
                f"📊 尝试的算法: {methods_text}"
            )
        
        if match_info.get("best_method"):
            await manager.send_log(
                websocket,
                "info",
                f"🎯 最佳匹配方法: {match_info['best_method']}"
            )
        
        if found:
            monitor_info = f"显示器 {location.get('monitor_id', 1)}" if location.get('monitor_id') else ""
            await manager.send_log(
                websocket, 
                "success", 
                f"✅ 找到目标图片！匹配度: {match_confidence:.2%} ({monitor_info})",
                {
                    "location": location,
                    "template_size": match_info.get("template_size"),
                    "method": match_info.get("best_method"),
                    "monitor_id": location.get('monitor_id'),
                    "monitor_name": location.get('monitor_name')
                }
            )
            
            # 显示所有显示器的搜索结果
            if match_info.get("monitor_results"):
                monitors_summary = []
                for mr in match_info["monitor_results"]:
                    monitors_summary.append(
                        f"显示器{mr['monitor_id']}: {mr['best_confidence']:.2%}"
                    )
                await manager.send_log(
                    websocket,
                    "info",
                    f"📺 各显示器匹配度: {', '.join(monitors_summary)}"
                )
            
            # 执行点击
            try:
                x = location['x']
                y = location['y']
                
                # 获取所有显示器信息用于验证
                monitors = get_all_monitors()
                
                # 计算所有显示器的总范围
                all_monitors_info = []
                for m in monitors:
                    all_monitors_info.append(
                        f"显示器{m['id']}[{m['left']},{m['top']}-{m['left']+m['width']},{m['top']+m['height']}]"
                    )
                
                await manager.send_log(
                    websocket,
                    "info",
                    f"📺 显示器范围: {', '.join(all_monitors_info)}"
                )
                
                # 验证坐标是否在任意显示器范围内
                coordinate_valid = False
                for m in monitors:
                    if (m['left'] <= x <= m['left'] + m['width'] and 
                        m['top'] <= y <= m['top'] + m['height']):
                        coordinate_valid = True
                        await manager.send_log(
                            websocket,
                            "info",
                            f"✅ 坐标在显示器{m['id']}范围内"
                        )
                        break
                
                if not coordinate_valid:
                    await manager.send_log(
                        websocket,
                        "warning",
                        f"⚠️ 坐标({x}, {y})可能超出显示器范围，但仍会尝试点击"
                    )
                    # 不再直接返回错误，而是继续尝试点击
                
                await manager.send_log(
                    websocket,
                    "info",
                    f"🖱️ 准备点击坐标: ({x}, {y})"
                )
                
                # 使用更安全的方式移动和点击
                # 先移动到位置（缓慢移动，避免触发系统手势）
                pyautogui.moveTo(x, y, duration=0.5, tween=pyautogui.easeInOutQuad)
                await asyncio.sleep(0.3)  # 增加等待时间，确保移动完成
                
                # 单独执行点击，不带任何修饰键
                pyautogui.click(x, y, clicks=1, interval=0.1, button='left')
                
                await manager.send_log(
                    websocket,
                    "success",
                    f"✅ 点击成功！位置: ({x}, {y})"
                )
                
                return {
                    "success": True,
                    "found": True,
                    "location": location,
                    "confidence": match_confidence,
                    "clicked": True
                }
                
            except Exception as e:
                await manager.send_log(
                    websocket,
                    "error",
                    f"❌ 点击失败: {str(e)}"
                )
                return {
                    "success": False,
                    "error": f"Click failed: {str(e)}"
                }
        else:
            await manager.send_log(
                websocket,
                "warning",
                f"⚠️ 未找到目标图片 (最高匹配度: {match_confidence:.2%})"
            )
            
            return {
                "success": False,
                "found": False,
                "confidence": match_confidence,
                "message": "图片未找到，请尝试降低置信度或使用更清晰的图片"
            }
            
    except Exception as e:
        if websocket:
            await manager.send_log(
                websocket,
                "error",
                f"❌ 执行出错: {str(e)}"
            )
        
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    PORT = 8899  # 使用不太常用的端口
    
    print("=" * 60)
    print("  py-picToWork 后端服务")
    print("=" * 60)
    print()
    print(f"📍 服务地址: http://localhost:{PORT}")
    print(f"📖 API 文档: http://localhost:{PORT}/docs")
    print()
    print("✨ 功能说明:")
    print(f"  1. 打开浏览器访问 http://localhost:{PORT}")
    print("  2. 上传要识别的图片（如按钮截图）")
    print("  3. 调整置信度参数（建议 0.7-0.9）")
    print("  4. 点击'识别并点击'按钮")
    print("  5. 系统将自动在屏幕上找到并点击目标")
    print()
    print("⚠️  注意:")
    print("  - macOS 需要授予辅助功能权限")
    print("  - 建议在测试前先截取目标按钮图片")
    print("  - 移动鼠标到屏幕角落可紧急停止")
    print()
    print(f"💡 提示: 如需更改端口，编辑 main.py 中的 PORT 变量")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )










