from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import os
import sys
import threading
import time
from typing import List, Dict, Any
import tempfile
import numpy as np
import urllib.parse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_processor_service import ImageFeatureExtractor
from services.search_service import SemanticSearchService

app = Flask(__name__)
# 配置CORS以允许前端访问，支持所有来源和方法
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3002", "http://localhost:5173", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 初始化服务
image_processor = ImageFeatureExtractor()
search_service = SemanticSearchService()

# 用于跟踪处理进度的字典
processing_status = {}

@app.after_request
def after_request(response):
    """为所有响应添加CORS头部"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return jsonify({"message": "Backend server is running!"})

@app.route('/api/extract-features', methods=['POST'])
def extract_features():
    """提取图像特征"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        
        if not image_path:
            return jsonify({"error": "Image path is required"}), 400
        
        features = image_processor.extract_features(image_path)
        return jsonify({"features": features, "path": image_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-by-text', methods=['POST'])
def search_by_text():
    """根据文本搜索"""
    try:
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('topK', 10)  # 获取返回结果数量，默认10
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        results = search_service.search_by_text(query, top_k=top_k)
        return jsonify({"results": results})
    except Exception as e:
        print(f"文本搜索API错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-by-image', methods=['POST'])
def search_by_image():
    """以图搜图 - 支持上传图片或使用本地路径"""
    try:
        if 'image' in request.files:
            # 情况1: 上传图片文件
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"error": "No image file provided"}), 400
            
            # 从查询参数或表单数据获取topK
            top_k = int(request.args.get('topK', 10))
            
            # 将上传的文件保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as temp_file:
                image_file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # 使用临时文件进行搜索
                results = search_service.search_by_image(temp_path, top_k=top_k)
                return jsonify({"results": results})
            finally:
                # 删除临时文件
                os.unlink(temp_path)
        else:
            # 情况2: 使用本地路径
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            image_path = data.get('imagePath')
            top_k = data.get('topK', 10)  # 获取返回结果数量，默认10
            
            if not image_path:
                return jsonify({"error": "Image path or file is required"}), 400
            
            results = search_service.search_by_image(image_path, top_k=top_k)
            return jsonify({"results": results})
    except Exception as e:
        print(f"搜索图片时出错: {str(e)}")  # 添加调试日志
        return jsonify({"error": str(e)}), 500

def process_folder_impl(folder_path: str, task_id: str, model: str = 'clip-vit-base-patch32'):
    """实际的文件夹处理实现"""
    global processing_status
    try:
        # 在处理开始时记录文件夹路径和模型
        processing_status[task_id] = {
            "status": "processing", 
            "progress": 0, 
            "total": 0, 
            "processed": 0, 
            "folderPath": folder_path,  # 添加文件夹路径
            "model": model  # 添加模型信息
        }
        
        # 获取文件夹中的所有图像文件
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        image_files = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        image_files.append(os.path.join(root, file))
        except PermissionError as e:
            print(f"权限不足，无法访问文件夹 {folder_path}: {e}")
            processing_status[task_id]["status"] = "failed"
            processing_status[task_id]["error"] = f"权限不足，无法访问文件夹: {str(e)}"
            return
        except Exception as e:
            print(f"扫描文件夹失败 {folder_path}: {e}")
            processing_status[task_id]["status"] = "failed"
            processing_status[task_id]["error"] = f"扫描文件夹失败: {str(e)}"
            return
        
        total_files = len(image_files)
        processing_status[task_id]["total"] = total_files
        
        # 逐个处理图像
        for i, image_path in enumerate(image_files):
            try:
                # 使用指定模型处理图像
                search_service.set_model(model)  # 设置模型
                search_service.add_image(image_path)
                processing_status[task_id]["processed"] = i + 1
                processing_status[task_id]["progress"] = int((i + 1) / total_files * 100)
            except Exception as e:
                print(f"处理图像失败 {image_path}: {e}")
        
        # 处理完成后更新状态
        processing_status[task_id]["status"] = "completed"
        processing_status[task_id]["folderPath"] = folder_path  # 确保路径仍然存在
        
        # 保存索引
        search_service.save_index()
        
    except Exception as e:
        processing_status[task_id]["status"] = "failed"
        processing_status[task_id]["error"] = str(e)
        processing_status[task_id]["folderPath"] = folder_path  # 确保路径仍然存在
        print(f"处理文件夹失败 {folder_path}: {e}")

@app.route('/api/process-folder', methods=['POST'])
def process_folder():
    """处理文件夹中的图像"""
    try:
        data = request.get_json()
        folder_path = data.get('folderPath')
        
        if not folder_path:
            return jsonify({"error": "Folder path is required"}), 400
        
        if not os.path.isdir(folder_path):
            return jsonify({"error": "Invalid folder path"}), 400
        
        # 生成任务ID
        task_id = f"task_{int(time.time())}"
        
        # 获取当前使用的模型
        current_model = search_service.current_model_name
        
        # 在新线程中处理文件夹
        thread = threading.Thread(target=process_folder_impl, args=(folder_path, task_id, current_model))
        thread.start()
        
        return jsonify({"taskId": task_id, "message": f"Started processing folder {folder_path}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/processing-status/<task_id>', methods=['GET'])
def get_processing_status(task_id: str):
    """获取文件夹处理状态"""
    global processing_status
    if task_id in processing_status:
        return jsonify(processing_status[task_id])
    else:
        return jsonify({"error": "Task not found"}), 404


@app.route('/api/reindex-folder', methods=['POST'])
def reindex_folder():
    """重新索引文件夹"""
    try:
        data = request.get_json()
        folder_path = data.get('folderPath')
        model = data.get('model', 'clip-vit-base-patch32')  # 默认模型
        
        if not folder_path:
            return jsonify({"error": "Folder path is required"}), 400
        
        if not os.path.isdir(folder_path):
            return jsonify({"error": "Invalid folder path"}), 400
        
        # 生成任务ID
        task_id = f"reindex_task_{int(time.time())}"
        
        # 在新线程中重新处理文件夹，传递模型参数
        thread = threading.Thread(target=process_folder_impl, args=(folder_path, task_id, model))
        thread.start()
        
        return jsonify({"taskId": task_id, "message": f"Started reindexing folder {folder_path} with model {model}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/thumbnails/<path:filename>', methods=['GET'])
def get_thumbnail(filename: str):
    """获取缩略图"""
    try:
        # 验证文件名安全
        if '..' in filename or filename.startswith('/'):
            return jsonify({"error": "Invalid filename"}), 400
        
        # 构建完整路径
        full_path = os.path.join(request.args.get('folder', ''), filename)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return jsonify({"error": "File not found"}), 404
        
        # 生成缩略图
        thumbnail_data = image_processor.generate_thumbnail(full_path)
        
        # 返回缩略图
        from io import BytesIO
        return send_file(
            BytesIO(thumbnail_data),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f"thumb_{os.path.basename(full_path)}"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image-proxy', methods=['GET'])
def image_proxy():
    """图片代理接口，用于前端显示本地图片"""
    try:
        image_path = request.args.get('path')
        if not image_path:
            return jsonify({"error": "Image path is required"}), 400
        
        # URL解码路径
        image_path = urllib.parse.unquote(image_path)
        
        # 验证路径安全性
        if not os.path.exists(image_path):
            return jsonify({"error": "Image not found"}), 404
        
        # 检查是否是图片文件
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        if not image_path.lower().endswith(image_extensions):
            return jsonify({"error": "Invalid image format"}), 400
        
        # 生成缩略图（用于快速加载）
        thumbnail_data = image_processor.generate_thumbnail(image_path, size=(300, 300))
        
        # 返回图片
        from io import BytesIO
        return send_file(
            BytesIO(thumbnail_data),
            mimetype='image/jpeg',
            as_attachment=False
        )
    except Exception as e:
        print(f"图片代理错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/image-info', methods=['POST'])
def get_image_info():
    """获取图像的详细信息，包括特征向量和可能的文本描述"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        
        print(f"收到图像信息请求，路径: {image_path}")
        
        if not image_path:
            return jsonify({"error": "Image path is required"}), 400
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"文件不存在: {image_path}")
            return jsonify({"error": "图像文件不存在"}), 404
        
        # 验证是否为图像文件
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        if not image_path.lower().endswith(image_extensions):
            print(f"不是有效的图像文件: {image_path}")
            return jsonify({"error": "不是有效的图像文件"}), 400
        
        # 获取图像特征向量
        try:
            features = search_service.encode_image(image_path)
            print(f"成功提取特征向量，维度: {len(features) if features is not None else 'None'}")
        except Exception as e:
            print(f"提取图像特征失败: {e}")
            return jsonify({"error": f"提取图像特征失败: {str(e)}"}), 500
        
        # 获取图像元数据
        try:
            metadata = image_processor.extract_metadata(image_path)
            print(f"成功获取元数据: {metadata}")
        except Exception as e:
            print(f"获取图像元数据失败: {e}")
            # 使用默认值继续处理
            metadata = {
                "width": 0,
                "height": 0,
                "format": "unknown",
                "size_bytes": os.path.getsize(image_path) if os.path.exists(image_path) else 0
            }
        
        # 尝试找到最相似的文本描述（通过预定义的描述词汇进行反向搜索）
        try:
            common_descriptions = [
                "一个人", "多个人", "风景", "建筑", "动物", "食物", "车辆", "花朵", "树木", "天空",
                "海洋", "山脉", "城市", "房屋", "道路", "桥梁", "公园", "森林", "沙滩", "雪景",
                "日落", "日出", "夜景", "室内", "户外", "儿童", "成人", "老人", "宠物", "鸟类",
                "猫", "狗", "汽车", "自行车", "飞机", "船只", "火车", "蛋糕", "水果", "蔬菜",
                "咖啡", "茶", "书籍", "电脑", "手机", "音乐", "运动", "游戏", "艺术", "雕塑"
            ]
            
            # 计算与各种描述的相似度
            best_descriptions = []
            for desc in common_descriptions:
                try:
                    desc_features = search_service.encode_text(desc)
                    # 计算余弦相似度
                    similarity = np.dot(features, desc_features) / (np.linalg.norm(features) * np.linalg.norm(desc_features))
                    if similarity > 0.2:  # 只保留相似度较高的描述
                        best_descriptions.append({
                            "description": desc,
                            "similarity": float(similarity)
                        })
                except Exception as e:
                    print(f"计算描述 '{desc}' 相似度时出错: {e}")
                    continue
            
            # 按相似度排序
            best_descriptions.sort(key=lambda x: x['similarity'], reverse=True)
            print(f"找到 {len(best_descriptions)} 个可能的描述")
        except Exception as e:
            print(f"生成文本描述时出错: {e}")
            best_descriptions = []
        
        return jsonify({
            "path": image_path,
            "metadata": metadata,
            "feature_vector_info": {
                "dimension": len(features),
                "model": "CLIP-ViT-B/32",
                "vector_norm": float(np.linalg.norm(features)) if features is not None else 0.0,
                "first_10_values": [float(x) for x in features[:10]] if features is not None else []  # 显示前10个值作为示例
            },
            "possible_descriptions": best_descriptions[:10]  # 返回前10个最相似的描述
        })
        
    except Exception as e:
        print(f"获取图像信息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/photos/timeline', methods=['GET'])
def get_photos_timeline():
    """获取按时间线组织的照片数据"""
    try:
        # 获取所有图片路径和元数据
        if not hasattr(search_service, 'image_paths') or not search_service.image_paths:
            return jsonify([])
        
        timeline_data = []
        from datetime import datetime
        import os
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        for image_path in search_service.image_paths:
            try:
                if not os.path.exists(image_path):
                    continue
                
                # 获取文件修改时间作为拍摄时间
                file_stat = os.stat(image_path)
                date_taken = datetime.fromtimestamp(file_stat.st_mtime)
                
                # 尝试从EXIF获取真实拍摄时间
                try:
                    with Image.open(image_path) as img:
                        exif_data = img._getexif()
                        if exif_data:
                            for tag_id, value in exif_data.items():
                                tag = TAGS.get(tag_id, tag_id)
                                if tag == "DateTime":
                                    try:
                                        date_taken = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                    except:
                                        pass
                except:
                    pass
                
                # 获取图片基本信息
                metadata = search_service.image_metadata.get(image_path, {})
                
                timeline_data.append({
                    "id": len(timeline_data),
                    "path": image_path,
                    "date": date_taken.isoformat(),
                    "title": os.path.basename(image_path),
                    "location": metadata.get("location", "未知位置"),
                    "tags": metadata.get("tags", []),
                    "metadata": metadata
                })
                
            except Exception as e:
                print(f"处理图片 {image_path} 时出错: {e}")
                continue
        
        # 按日期排序
        timeline_data.sort(key=lambda x: x["date"], reverse=True)
        
        return jsonify(timeline_data)
        
    except Exception as e:
        print(f"获取时间线数据失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/photos/location', methods=['GET'])
def get_photos_location():
    """获取按地理位置组织的照片数据"""
    try:
        if not hasattr(search_service, 'image_paths') or not search_service.image_paths:
            return jsonify([])
        
        location_data = {}
        
        for image_path in search_service.image_paths:
            try:
                if not os.path.exists(image_path):
                    continue
                
                metadata = search_service.image_metadata.get(image_path, {})
                location = metadata.get("location", "未知位置")
                
                if location not in location_data:
                    location_data[location] = {
                        "name": location,
                        "images": [],
                        "count": 0
                    }
                
                location_data[location]["images"].append({
                    "path": image_path,
                    "title": os.path.basename(image_path),
                    "metadata": metadata
                })
                location_data[location]["count"] += 1
                
            except Exception as e:
                print(f"处理图片 {image_path} 时出错: {e}")
                continue
        
        # 转换为列表格式
        result = list(location_data.values())
        # 按图片数量排序
        result.sort(key=lambda x: x["count"], reverse=True)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取地理位置数据失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/photos/people', methods=['GET'])
def get_photos_people():
    """获取按人物组织的照片数据"""
    try:
        if not hasattr(search_service, 'image_paths') or not search_service.image_paths:
            return jsonify([])
        
        # 模拟人物数据，实际应该使用人脸识别
        people_data = [
            {
                "id": 1,
                "name": "未识别人物",
                "images": [],
                "count": 0
            }
        ]
        
        for image_path in search_service.image_paths:
            try:
                if not os.path.exists(image_path):
                    continue
                
                metadata = search_service.image_metadata.get(image_path, {})
                
                # 简单检测是否包含人物（基于文件名或路径）
                if any(keyword in image_path.lower() for keyword in ['person', 'people', 'portrait', '人物', '肖像']):
                    people_data[0]["images"].append({
                        "path": image_path,
                        "title": os.path.basename(image_path),
                        "metadata": metadata
                    })
                    people_data[0]["count"] += 1
                
            except Exception as e:
                print(f"处理图片 {image_path} 时出错: {e}")
                continue
        
        # 过滤掉没有图片的人物
        result = [person for person in people_data if person["count"] > 0]
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取人物数据失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/validate-folder', methods=['POST'])
def validate_folder():
    """验证文件夹是否存在且包含支持的图片文件"""
    try:
        data = request.get_json()
        folder_path = data.get('folderPath')
        
        if not folder_path:
            return jsonify({"valid": False, "error": "未提供文件夹路径"}), 400
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return jsonify({"valid": False, "error": "文件夹不存在"}), 200
        
        if not os.path.isdir(folder_path):
            return jsonify({"valid": False, "error": "路径不是文件夹"}), 200
        
        # 支持的图片格式
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        
        # 扫描文件夹中的图片文件
        image_files = []
        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(image_extensions):
                    image_files.append(filename)
        except PermissionError:
            # 权限不足时，仍然允许用户尝试添加文件夹
            # 后端处理时会再次检查权限
            return jsonify({
                "valid": True, 
                "imageCount": 0,
                "message": "无法扫描文件夹内容，但可以尝试添加",
                "warning": "权限不足，将在处理时再次检查"
            })
        
        if not image_files:
            return jsonify({"valid": False, "error": "该文件夹中未找到支持的图片文件"}), 200
        
        return jsonify({
            "valid": True,
            "imageCount": len(image_files),
            "message": f"找到 {len(image_files)} 个图片文件"
        })
        
    except Exception as e:
        print(f"验证文件夹失败: {e}")
        return jsonify({"valid": False, "error": "验证文件夹时发生错误"}), 500

@app.route('/api/get-model', methods=['GET'])
def get_current_model():
    """获取当前使用的AI模型信息"""
    try:
        current_model_name = search_service.current_model_name
        
        # 模型名称映射到显示名称
        model_display_names = {
            'openai/clip-vit-base-patch32': 'CLIP ViT-B/32',
            'openai/clip-vit-large-patch14': 'CLIP ViT-L/14',
            'OFA-Sys/chinese-clip-vit-base-patch16': 'Chinese CLIP ViT-B/16',
            'sentence-transformers/clip-ViT-B-32-multilingual-v1': 'Multilingual CLIP ViT-B/32',
            'Salesforce/blip-image-captioning-base': 'BLIP Base'
        }
        
        display_name = model_display_names.get(current_model_name, current_model_name)
        
        return jsonify({
            "model_id": current_model_name,
            "display_name": display_name,
            "index_count": search_service.index.ntotal if search_service.index else 0
        })
        
    except Exception as e:
        print(f"获取模型信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/set-model', methods=['POST'])
def set_model():
    """设置AI模型"""
    try:
        data = request.get_json()
        model_name = data.get('model')
        
        if not model_name:
            return jsonify({"error": "未提供模型名称"}), 400
        
        print(f"收到模型切换请求: {model_name}")
        
        # 检查模型是否有效
        valid_models = [
            'clip-vit-base-patch32',
            'clip-vit-large-patch14', 
            'chinese-clip-vit-base-patch16',
            'multilingual-clip-vit-base-patch32',
            'blip-base'
        ]
        
        if model_name not in valid_models:
            return jsonify({"error": f"无效的模型名称: {model_name}"}), 400
        
        # 切换模型
        old_model = search_service.current_model_name
        search_service.set_model(model_name)
        
        # 检查是否需要重建索引
        needs_rebuild = search_service.index.ntotal > 0
        
        if needs_rebuild:
            # 生成重建任务ID
            rebuild_task_id = f"rebuild_model_{int(time.time())}"
            
            # 在后台线程中重建索引
            def rebuild_index_task():
                try:
                    processing_status[rebuild_task_id] = {
                        "status": "processing",
                        "progress": 0,
                        "total": search_service.index.ntotal,
                        "processed": 0,
                        "message": f"正在使用新模型 {model_name} 重建索引..."
                    }
                    
                    search_service.rebuild_index_with_new_model_progress(rebuild_task_id, processing_status)
                    
                    processing_status[rebuild_task_id]["status"] = "completed"
                    processing_status[rebuild_task_id]["message"] = "索引重建完成"
                    
                except Exception as e:
                    processing_status[rebuild_task_id]["status"] = "failed"
                    processing_status[rebuild_task_id]["message"] = f"索引重建失败: {str(e)}"
                    print(f"索引重建失败: {e}")
            
            thread = threading.Thread(target=rebuild_index_task)
            thread.start()
            
            return jsonify({
                "message": f"模型已切换为 {model_name}",
                "rebuildTaskId": rebuild_task_id,
                "needsRebuild": True,
                "oldModel": old_model,
                "newModel": model_name
            })
        else:
            return jsonify({
                "message": f"模型已切换为 {model_name}",
                "needsRebuild": False,
                "oldModel": old_model,
                "newModel": model_name
            })
            
    except Exception as e:
        print(f"设置模型失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """根据照片生成故事"""
    try:
        data = request.get_json()
        photo_ids = data.get('photoIds', [])
        
        if not photo_ids:
            return jsonify({"error": "未提供照片ID"}), 400
        
        # 模拟故事生成逻辑
        import random
        from datetime import datetime
        
        story_templates = [
            "这是一个关于美好时光的故事。在这些珍贵的瞬间里，记录了生活中的点点滴滴。",
            "时光荏苒，这些照片见证了许多难忘的回忆。每一张图片都诉说着独特的故事。",
            "在这个特别的时刻，镜头捕捉到了最真实的情感。这些画面将永远珍藏在心中。",
            "生活就像一本相册，每一页都记录着不同的精彩。这些照片串联起了美好的回忆。"
        ]
        
        locations = ["公园", "海边", "山顶", "城市", "家中", "咖啡厅", "学校", "办公室"]
        emotions = ["快乐", "温馨", "宁静", "激动", "感动", "惊喜", "满足", "幸福"]
        
        # 生成故事内容
        story_content = random.choice(story_templates)
        story_location = random.choice(locations)
        story_emotion = random.choice(emotions)
        
        # 构建完整故事
        full_story = f"在{story_location}，{story_content} 整个过程充满了{story_emotion}的氛围，让人回味无穷。"
        
        # 获取相关照片信息
        story_images = []
        for photo_id in photo_ids[:10]:  # 最多处理10张照片
            try:
                photo_index = int(photo_id)
                if 0 <= photo_index < len(search_service.image_paths):
                    image_path = search_service.image_paths[photo_index]
                    if os.path.exists(image_path):
                        story_images.append({
                            "id": photo_id,
                            "path": image_path,
                            "title": os.path.basename(image_path)
                        })
            except (ValueError, IndexError):
                continue
        
        result = {
            "id": f"story_{int(datetime.now().timestamp())}",
            "title": f"AI生成故事 - {story_emotion}的{story_location}时光",
            "content": full_story,
            "images": story_images,
            "created_at": datetime.now().isoformat(),
            "tags": [story_location, story_emotion, "AI生成"],
            "summary": f"包含{len(story_images)}张照片的{story_emotion}故事"
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"生成故事失败: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=9527)