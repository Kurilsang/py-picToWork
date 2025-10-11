"""
改进的图像匹配模块 - 支持多显示器、多算法、多尺度
"""
import cv2
import numpy as np
from datetime import datetime
import os


def enhance_image(img):
    """增强图像对比度"""
    try:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    except:
        return img


def match_template_multi_method(screenshot_gray, template_gray):
    """
    使用多种算法进行模板匹配
    返回: (best_match_loc, best_confidence, best_method, all_results)
    """
    best_match = None
    best_confidence = 0.0
    best_method = None
    all_results = []
    
    methods = [
        ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
        ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
        ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
    ]
    
    for method_name, method in methods:
        try:
            result = cv2.matchTemplate(screenshot_gray, template_gray, method)
            
            if method == cv2.TM_SQDIFF_NORMED:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                match_val = 1 - min_val
                match_loc = min_loc
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                match_val = max_val
                match_loc = max_loc
            
            all_results.append({
                "method": method_name,
                "confidence": float(match_val)
            })
            
            if match_val > best_confidence:
                best_confidence = match_val
                best_match = match_loc
                best_method = method_name
        except Exception as e:
            all_results.append({
                "method": method_name,
                "error": str(e)
            })
    
    return best_match, best_confidence, best_method, all_results


def match_template_multi_scale(screenshot_gray, template_gray, base_confidence):
    """
    多尺度模板匹配
    返回: (best_match_loc, best_confidence, best_method, scale_results)
    """
    best_match = None
    best_confidence = base_confidence
    best_method = None
    scale_results = []
    best_template = template_gray
    
    scales = [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]
    
    for scale in scales:
        try:
            width = int(template_gray.shape[1] * scale)
            height = int(template_gray.shape[0] * scale)
            
            if width < 10 or height < 10 or width > screenshot_gray.shape[1] or height > screenshot_gray.shape[0]:
                continue
            
            template_scaled = cv2.resize(template_gray, (width, height))
            result = cv2.matchTemplate(screenshot_gray, template_scaled, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            scale_results.append({
                "scale": scale,
                "confidence": float(max_val)
            })
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = max_loc
                best_method = f"Multi-scale ({scale}x)"
                best_template = template_scaled
        except Exception as e:
            scale_results.append({
                "scale": scale,
                "error": str(e)
            })
    
    return best_match, best_confidence, best_method, scale_results, best_template


def find_image_on_screen_multi_monitor(screenshots, template_path, confidence=0.8, enable_debug=False):
    """
    在多个显示器上查找图片
    screenshots: 显示器截图列表
    返回: (found, location, match_confidence, match_info)
    """
    # 加载模板图片
    template = cv2.imread(template_path)
    if template is None:
        return False, None, 0.0, {"error": "无法加载模板图片"}
    
    # 初始化匹配信息
    match_info = {
        "template_size": f"{template.shape[1]}x{template.shape[0]}",
        "monitors_searched": len(screenshots),
        "monitor_results": []
    }
    
    # 全局最佳匹配
    global_best_match = None
    global_best_confidence = 0.0
    global_best_monitor = None
    global_best_method = None
    global_template_size = None
    
    # 预处理模板
    template_enhanced = enhance_image(template)
    template_gray = cv2.cvtColor(template_enhanced, cv2.COLOR_BGR2GRAY)
    
    # 遍历所有显示器
    for screen_data in screenshots:
        screenshot = screen_data["image"]
        monitor_id = screen_data["monitor_id"]
        offset_x = screen_data["offset_x"]
        offset_y = screen_data["offset_y"]
        
        # 预处理屏幕截图
        screenshot_enhanced = enhance_image(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_enhanced, cv2.COLOR_BGR2GRAY)
        
        # 使用多算法匹配
        match_loc, match_conf, match_method, method_results = match_template_multi_method(
            screenshot_gray, template_gray
        )
        
        monitor_result = {
            "monitor_id": monitor_id,
            "monitor_size": f"{screen_data['width']}x{screen_data['height']}",
            "offset": f"({offset_x}, {offset_y})",
            "methods_tried": method_results,
            "best_confidence": float(match_conf)
        }
        
        # 如果置信度不够，尝试多尺度匹配
        final_template = template_gray
        if match_conf < confidence and match_conf > 0.5:
            scale_match, scale_conf, scale_method, scale_results, scaled_template = match_template_multi_scale(
                screenshot_gray, template_gray, match_conf
            )
            
            monitor_result["multi_scale_tried"] = scale_results
            
            if scale_conf > match_conf:
                match_loc = scale_match
                match_conf = scale_conf
                match_method = scale_method
                final_template = scaled_template
                monitor_result["best_confidence"] = float(scale_conf)
        
        monitor_result["best_method"] = match_method
        match_info["monitor_results"].append(monitor_result)
        
        # 更新全局最佳匹配
        if match_conf > global_best_confidence:
            global_best_confidence = match_conf
            global_best_match = match_loc
            global_best_monitor = screen_data
            global_best_method = match_method
            global_template_size = (final_template.shape[1], final_template.shape[0])
    
    # 设置全局匹配信息
    match_info["best_confidence"] = float(global_best_confidence)
    match_info["best_method"] = global_best_method
    
    # 判断是否找到
    if global_best_match and global_best_confidence >= confidence:
        h, w = global_template_size
        
        # 计算绝对屏幕坐标（考虑显示器偏移）
        absolute_x = global_best_match[0] + global_best_monitor["offset_x"] + w // 2
        absolute_y = global_best_match[1] + global_best_monitor["offset_y"] + h // 2
        
        location = {
            "x": int(absolute_x),
            "y": int(absolute_y),
            "width": int(w),
            "height": int(h),
            "monitor_id": global_best_monitor["monitor_id"],
            "monitor_name": f"显示器 {global_best_monitor['monitor_id']}",
            "local_x": int(global_best_match[0] + w // 2),  # 显示器内的相对坐标
            "local_y": int(global_best_match[1] + h // 2),
            "top_left": {
                "x": int(global_best_match[0] + global_best_monitor["offset_x"]),
                "y": int(global_best_match[1] + global_best_monitor["offset_y"])
            },
            "bottom_right": {
                "x": int(global_best_match[0] + global_best_monitor["offset_x"] + w),
                "y": int(global_best_match[1] + global_best_monitor["offset_y"] + h)
            }
        }
        
        # 调试模式：保存匹配结果
        if enable_debug:
            try:
                debug_img = global_best_monitor["image"].copy()
                cv2.rectangle(
                    debug_img,
                    (global_best_match[0], global_best_match[1]),
                    (global_best_match[0] + w, global_best_match[1] + h),
                    (0, 255, 0), 3
                )
                cv2.putText(
                    debug_img,
                    f"Monitor {global_best_monitor['monitor_id']}: {global_best_confidence:.2%}",
                    (global_best_match[0], global_best_match[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
                debug_path = os.path.join("backend/uploads", 
                                        f"debug_match_{datetime.now().strftime('%H%M%S')}.png")
                cv2.imwrite(debug_path, debug_img)
                match_info["debug_image"] = debug_path
            except:
                pass
        
        return True, location, float(global_best_confidence), match_info
    
    return False, None, float(global_best_confidence), match_info

