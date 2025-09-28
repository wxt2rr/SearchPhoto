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
            
            # 将上传的文件保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as temp_file:
                image_file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # 使用临时文件进行搜索
                results = search_service.search_by_image(temp_path, top_k=request.json.get('topK', 10) if request.json else 10)
                return jsonify({"results": results})
            finally:
                # 删除临时文件
                os.unlink(temp_path)
        else:
            # 情况2: 使用本地路径
            data = request.get_json()
            image_path = data.get('imagePath')
            top_k = data.get('topK', 10)  # 获取返回结果数量，默认10
            
            if not image_path:
                return jsonify({"error": "Image path or file is required"}), 400
            
            results = search_service.search_by_image(image_path, top_k=top_k)
            return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_folder_impl(folder_path: str, task_id: str):
    """实际的文件夹处理实现"""
    global processing_status
    try:
        # 在处理开始时记录文件夹路径
        processing_status[task_id] = {
            "status": "processing", 
            "progress": 0, 
            "total": 0, 
            "processed": 0, 
            "folderPath": folder_path  # 添加文件夹路径
        }
        
        # 获取文件夹中的所有图像文件
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        image_files = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(image_extensions):
                    image_files.append(os.path.join(root, file))
        
        total_files = len(image_files)
        processing_status[task_id]["total"] = total_files
        
        # 逐个处理图像
        for i, image_path in enumerate(image_files):
            try:
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
        
        # 在新线程中处理文件夹
        thread = threading.Thread(target=process_folder_impl, args=(folder_path, task_id))
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)