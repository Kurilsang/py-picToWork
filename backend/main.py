#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
py-picToWork 简化版后端
实现图片识别和自动点击功能 - 优化整合版
"""

# ==============================
# 导入模块
# ==============================
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
import pyautogui
import mss
from PIL import Image
from typing import List, Dict, Optional, Tuple, Any
import asyncio
import json
from datetime import datetime
import os
import platform
from dataclasses import dataclass
import warnings

# ==============================
# 配置定义
# ==============================
@dataclass
class AppConfig:
    """应用配置类"""
    # 服务配置
    PORT: int = 8899
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "info"
    
    # 路径配置
    UPLOAD_DIR: str = "backend/uploads"
    STATIC_DIR: str = "static"
    
    # 图像识别配置
    DEFAULT_CONFIDENCE: float = 0.8
    MIN_CONFIDENCE: float = 0.0
    MAX_CONFIDENCE: float = 1.0
    
    # PyAutoGUI 配置
    PYAUTOGUI_PAUSE: float = 0.1
    PYAUTOGUI_FAILSAFE: bool = True
    MOVE_DURATION: float = 0.5
    CLICK_INTERVAL: float = 0.1
    
    # WebSocket 配置
    WS_RECONNECT_DELAY: int = 5  # 重连延迟（秒）

# 初始化配置实例
app_config = AppConfig()

# 系统相关配置
SYSTEM = platform.system()
IS_MACOS = SYSTEM == "Darwin"
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"

# ==============================
# 工具函数
# ==============================
def ensure_dir(dir_path: str) -> None:
    """确保目录存在，不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def save_uploaded_file(file_content: bytes, file_ext: str = "png") -> str:
    """保存上传的文件"""
    ensure_dir(app_config.UPLOAD_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_name = f"target_{timestamp}.{file_ext}"
    file_path = os.path.join(app_config.UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path

def get_all_monitors() -> List[Dict]:
    """获取所有显示器信息"""
    with mss() as sct:
        monitors = []
        for i, monitor in enumerate(sct.monitors[1:], 1):  # 跳过第0个（全屏）
            monitors.append({
                "id": i,
                "left": monitor["left"],
                "top": monitor["top"],
                "width": monitor["width"],
                "height": monitor["height"],
                "name": f"显示器 {i}",
                "bounds": (
                    monitor["left"], 
                    monitor["top"], 
                    monitor["left"] + monitor["width"], 
                    monitor["top"] + monitor["height"]
                )
            })
        return monitors

def capture_screenshot(monitor_id: Optional[int] = None) -> List[Dict]:
    """
    截取屏幕
    :param monitor_id: None表示所有显示器，数字表示指定显示器
    :return: 图片列表，包含图片数据和显示器信息
    """
    with mss() as sct:
        screenshots = []
        
        if monitor_id is None:
            # 截取所有显示器
            target_monitors = sct.monitors[1:]
        else:
            # 截取指定显示器
            if monitor_id < 1 or monitor_id >= len(sct.monitors):
                monitor_id = 1  # 默认主显示器
            target_monitors = [sct.monitors[monitor_id]]
        
        for i, monitor in enumerate(target_monitors, 1):
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            screenshots.append({
                "monitor_id": i,
                "image": img,
                "offset_x": monitor["left"],
                "offset_y": monitor["top"],
                "width": monitor["width"],
                "height": monitor["height"],
                "monitor_info": monitor
            })
        
        return screenshots

def validate_coordinates(x: float, y: float, monitors: List[Dict]) -> Tuple[bool, Optional[Dict]]:
    """验证坐标是否在显示器范围内"""
    for monitor in monitors:
        left, top, right, bottom = monitor["bounds"]
        if left <= x <= right and top <= y <= bottom:
            return True, monitor
    return False, None

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return filename.split(".")[-1].lower() if "." in filename else "png"

def validate_image_file(filename: str, content_type: str) -> bool:
    """验证是否为合法的图片文件"""
    allowed_extensions = {"png", "jpg", "jpeg", "bmp", "gif"}
    allowed_content_types = {"image/png", "image/jpeg", "image/bmp", "image/gif"}
    
    file_ext = get_file_extension(filename)
    return file_ext in allowed_extensions and content_type in allowed_content_types

# ==============================
# 图像匹配模块（内置实现）
# ==============================
def find_image_on_screen_multi_monitor(
    screenshots: List[Dict],
    template_path: str,
    confidence: float = 0.8,
    enable_debug: bool = False
) -> Tuple[bool, Optional[Dict], float, Dict]:
    """
    多显示器图像匹配实现
    :param screenshots: 屏幕截图列表
    :param template_path: 模板图片路径
    :param confidence: 置信度阈值
    :param enable_debug: 是否启用调试模式
    :return: (是否找到, 位置信息, 最佳匹配度, 匹配详情)
    """
    # 读取模板图片
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法读取模板图片: {template_path}")
    
    template_height, template_width = template.shape[:2]
    template_size = (template_width, template_height)
    
    best_confidence = 0.0
    best_location = None
    best_monitor_id = 1
    method_results = []
    monitor_results = []
    
    # 定义要尝试的匹配算法
    match_methods = [
        (cv2.TM_CCOEFF_NORMED, "TM_CCOEFF_NORMED"),
        (cv2.TM_CCORR_NORMED, "TM_CCORR_NORMED"),
        (cv2.TM_SQDIFF_NORMED, "TM_SQDIFF_NORMED")
    ]
    
    for screen in screenshots:
        screen_img = screen["image"]
        screen_height, screen_width = screen_img.shape[:2]
        monitor_id = screen["monitor_id"]
        
        # 如果模板比屏幕大，跳过
        if template_width > screen_width or template_height > screen_height:
            if enable_debug:
                monitor_results.append({
                    "monitor_id": monitor_id,
                    "best_confidence": 0.0,
                    "message": "模板尺寸大于屏幕尺寸"
                })
            continue
        
        monitor_best_confidence = 0.0
        monitor_best_loc = None
        monitor_best_method = None
        
        for method, method_name in match_methods:
            try:
                # 执行模板匹配
                result = cv2.matchTemplate(screen_img, template, method)
                
                # 根据方法类型获取匹配值
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                    # 平方差方法，值越小越好
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    current_confidence = 1 - min_val  # 转换为相似度（1为最佳）
                    top_left = min_loc
                else:
                    # 其他方法，值越大越好
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    current_confidence = max_val
                    top_left = max_loc
                
                method_results.append({
                    "method": method_name,
                    "confidence": current_confidence,
                    "monitor_id": monitor_id
                })
                
                # 更新当前显示器的最佳匹配
                if current_confidence > monitor_best_confidence:
                    monitor_best_confidence = current_confidence
                    monitor_best_loc = top_left
                    monitor_best_method = method_name
                
            except Exception as e:
                if enable_debug:
                    method_results.append({
                        "method": method_name,
                        "confidence": 0.0,
                        "error": str(e)
                    })
        
        # 更新全局最佳匹配
        if monitor_best_confidence > best_confidence and monitor_best_confidence > best_confidence:
            best_confidence = monitor_best_confidence
            best_monitor_id = monitor_id
            
            # 计算中心点坐标（全局坐标）
            center_x = screen["offset_x"] + monitor_best_loc[0] + template_width // 2
            center_y = screen["offset_y"] + monitor_best_loc[1] + template_height // 2
            
            best_location = {
                "x": center_x,
                "y": center_y,
                "local_x": monitor_best_loc[0],
                "local_y": monitor_best_loc[1],
                "width": template_width,
                "height": template_height,
                "top_left": (screen["offset_x"] + monitor_best_loc[0], screen["offset_y"] + monitor_best_loc[1]),
                "monitor_id": monitor_id,
                "monitor_name": f"显示器 {monitor_id}"
            }
        
        monitor_results.append({
            "monitor_id": monitor_id,
            "best_confidence": monitor_best_confidence,
            "best_method": monitor_best_method
        })
    
    # 确定最终结果
    found = best_confidence >= confidence
    
    match_info = {
        "template_size": template_size,
        "methods_tried": method_results,
        "best_method": next(
            (m["method"] for m in method_results if m["confidence"] == best_confidence),
            None
        ),
        "monitor_results": monitor_results,
        "debug": enable_debug
    }
    
    return found, best_location, best_confidence, match_info

# ==============================
# WebSocket 连接管理
# ==============================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_log(websocket, "info", "WebSocket 连接成功")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_log(
        self, 
        websocket: WebSocket, 
        level: str, 
        message: str, 
        data: Optional[Dict] = None
    ):
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
        except Exception:
            # 忽略发送失败的情况
            pass

# 初始化WebSocket管理器
ws_manager = ConnectionManager()

# ==============================
# PyAutoGUI 初始化配置
# ==============================
# 基础安全配置
pyautogui.FAILSAFE = app_config.PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = app_config.PYAUTOGUI_PAUSE

# macOS 特殊配置
if IS_MACOS:
    warnings.filterwarnings('ignore', category=DeprecationWarning)

# ==============================
# FastAPI 应用初始化
# ==============================
app = FastAPI(title="py-picToWork MVP", description="基于图像识别的屏幕自动化操作工具")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 图像识别包装函数
# ==============================
def find_image_on_screen(
    template_path: str,
    confidence: float = 0.8,
    enable_debug: bool = False,
    monitor_id: Optional[int] = None
) -> Tuple[bool, Optional[Dict], float, Dict]:
    """
    图像识别包装函数 - 支持多尺度、多算法和多显示器匹配
    :param template_path: 模板图片路径
    :param confidence: 置信度阈值
    :param enable_debug: 是否启用调试模式
    :param monitor_id: 监控器ID，None表示所有
    :return: (是否找到, 位置信息, 匹配置信度, 匹配详情)
    """
    # 截取屏幕（单个或所有显示器）
    screenshots = capture_screenshot(monitor_id)
    
    # 调用图像匹配模块
    return find_image_on_screen_multi_monitor(screenshots, template_path, confidence, enable_debug)

# ==============================
# API 路由
# ==============================
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
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # 保持连接
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.post("/api/execute")
async def execute_task(
    file: UploadFile = File(...),
    confidence: float = Form(app_config.DEFAULT_CONFIDENCE)
):
    """
    执行识别和点击任务
    """
    # 验证WebSocket连接
    if not ws_manager.active_connections:
        return {"success": False, "error": "No WebSocket connection"}
    
    websocket = ws_manager.active_connections[0]
    
    try:
        # 验证图片文件
        if not validate_image_file(file.filename, file.content_type):
            await ws_manager.send_log(websocket, "error", f"❌ 不支持的文件格式: {file.filename}")
            return {"success": False, "error": "Unsupported file format"}
        
        # 验证置信度参数
        confidence = max(app_config.MIN_CONFIDENCE, min(app_config.MAX_CONFIDENCE, confidence))
        
        # 保存上传的图片
        file_ext = get_file_extension(file.filename)
        file_content = await file.read()
        file_path = save_uploaded_file(file_content, file_ext)
        
        await ws_manager.send_log(websocket, "info", f"📁 图片已保存: {file.filename}")
        
        # 获取显示器信息
        monitors = get_all_monitors()
        monitor_summary = ", ".join([f"显示器{m['id']}({m['width']}x{m['height']})" for m in monitors])
        await ws_manager.send_log(websocket, "info", f"🖥️ 检测到 {len(monitors)} 个显示器: {monitor_summary}")
        
        await ws_manager.send_log(websocket, "info", f"🔍 开始识别屏幕 (置信度: {confidence})")
        await ws_manager.send_log(websocket, "info", "🔬 使用多算法和多尺度匹配...")
        
        # 查找图片（启用调试模式）
        found, location, match_confidence, match_info = find_image_on_screen(
            file_path, confidence, enable_debug=True
        )
        
        # 输出详细的坐标信息用于调试
        if found and location:
            await ws_manager.send_log(
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
            await ws_manager.send_log(
                websocket,
                "info",
                f"📊 尝试的算法: {methods_text}"
            )
        
        if match_info.get("best_method"):
            await ws_manager.send_log(
                websocket,
                "info",
                f"🎯 最佳匹配方法: {match_info['best_method']}"
            )
        
        if found:
            monitor_info = f"显示器 {location.get('monitor_id', 1)}" if location.get('monitor_id') else ""
            await ws_manager.send_log(
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
                await ws_manager.send_log(
                    websocket,
                    "info",
                    f"📺 各显示器匹配度: {', '.join(monitors_summary)}"
                )
            
            # 执行点击
            try:
                x = location['x']
                y = location['y']
                
                # 验证坐标是否在显示器范围内
                coordinate_valid, target_monitor = validate_coordinates(x, y, monitors)
                
                if coordinate_valid and target_monitor:
                    await ws_manager.send_log(
                        websocket,
                        "info",
                        f"✅ 坐标在{target_monitor['name']}范围内"
                    )
                else:
                    await ws_manager.send_log(
                        websocket,
                        "warning",
                        f"⚠️ 坐标({x}, {y})可能超出显示器范围，但仍会尝试点击"
                    )
                
                await ws_manager.send_log(
                    websocket,
                    "info",
                    f"🖱️ 准备点击坐标: ({x}, {y})"
                )
                
                # 使用更安全的方式移动和点击
                pyautogui.moveTo(x, y, duration=app_config.MOVE_DURATION, tween=pyautogui.easeInOutQuad)
                await asyncio.sleep(0.3)  # 增加等待时间，确保移动完成
                
                # 单独执行点击，不带任何修饰键
                pyautogui.click(x, y, clicks=1, interval=app_config.CLICK_INTERVAL, button='left')
                
                await ws_manager.send_log(
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
                await ws_manager.send_log(
                    websocket,
                    "error",
                    f"❌ 点击失败: {str(e)}"
                )
                return {
                    "success": False,
                    "error": f"Click failed: {str(e)}"
                }
        else:
            await ws_manager.send_log(
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
        await ws_manager.send_log(
            websocket,
            "error",
            f"❌ 执行出错: {str(e)}"
        )
        
        return {
            "success": False,
            "error": str(e)
        }

# ==============================
# 启动入口
# ==============================
if __name__ == "__main__":
    print("=" * 60)
    print("  py-picToWork 后端服务 (优化版)")
    print("=" * 60)
    print()
    print(f"📍 服务地址: http://localhost:{app_config.PORT}")
    print(f"📖 API 文档: http://localhost:{app_config.PORT}/docs")
    print()
    print("✨ 功能说明:")
    print(f"  1. 打开浏览器访问 http://localhost:{app_config.PORT}")
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
    print(f"💡 提示: 如需更改端口，编辑代码中的 PORT 配置")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host=app_config.HOST,
        port=app_config.PORT,
        log_level=app_config.LOG_LEVEL
    )
