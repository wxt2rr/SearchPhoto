import os
import sys
import pickle
import faiss
import numpy as np
import time
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel, ChineseCLIPProcessor, ChineseCLIPModel
import torch
from PIL import Image
from models.search_service import SearchServiceInterface

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SemanticSearchService(SearchServiceInterface):
    """语义搜索服务实现"""
    
    def __init__(self, index_path: str = "image_index.faiss", metadata_path: str = "image_metadata.pkl"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model_info_path = "model_info.pkl"  # 新增：存储模型信息
        
        # 当前使用的模型名称
        self.current_model_name = "openai/clip-vit-base-patch32"
        
        # 加载文本编码模型
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 加载CLIP模型用于图像特征提取
        self.clip_model = CLIPModel.from_pretrained(self.current_model_name)
        self.clip_processor = CLIPProcessor.from_pretrained(self.current_model_name)
        self.clip_model.eval()
        
        # 初始化FAISS索引
        self.index = None
        self.image_metadata = {}  # 存储图像元数据
        self.image_paths = []  # 存储图像路径列表，用于索引映射
        
        # 尝试加载现有的索引
        self.load_index()
    
    def load_index(self):
        """加载已保存的索引"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # 检查模型信息
                index_model_name = self._get_index_model_name()
                
                if index_model_name and index_model_name != self.current_model_name:
                    print(f"⚠️  检测到模型不匹配:")
                    print(f"   索引模型: {index_model_name}")
                    print(f"   当前模型: {self.current_model_name}")
                    print("   需要重新构建索引以确保搜索准确性")
                    
                    # 创建新的空索引
                    dimension = 512
                    self.index = faiss.IndexFlatIP(dimension)
                    self.image_metadata = {}
                    self.image_paths = []
                    return
                
                # 加载索引
                self.index = faiss.read_index(self.index_path)
                
                with open(self.metadata_path, 'rb') as f:
                    self.image_metadata = pickle.load(f)
                
                # 重建图像路径列表
                self.image_paths = list(self.image_metadata.keys())
                
                print(f"索引加载成功，包含 {self.index.ntotal} 张图像，使用模型: {self.current_model_name}")
            else:
                print("未找到现有索引，将创建新的索引")
                # 创建新的FAISS索引（CLIP模型的特征维度是512）
                dimension = 512
                self.index = faiss.IndexFlatIP(dimension)
        except Exception as e:
            print(f"加载索引失败: {e}")
            # 创建新的索引
            dimension = 512
            self.index = faiss.IndexFlatIP(dimension)
    
    def save_index(self):
        """保存索引到文件"""
        try:
            faiss.write_index(self.index, self.index_path)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.image_metadata, f)
            
            # 保存模型信息
            self._save_model_info()
            
            print(f"索引已保存，包含 {self.index.ntotal} 张图像，使用模型: {self.current_model_name}")
        except Exception as e:
            print(f"保存索引失败: {e}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """将文本编码为向量"""
        try:
            print(f"编码文本: '{text}'")
            
            # 最简化处理：直接使用原始查询文本，不进行任何翻译或转换
            # 这样可以避免所有潜在的问题
            inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
            
            with torch.no_grad():
                text_features = self.clip_model.get_text_features(**inputs)
            
            # 将特征转换为numpy数组并归一化
            features = text_features.squeeze().cpu().numpy()
            features = features / np.linalg.norm(features)
            
            print(f"文本编码完成，特征维度: {features.shape}, 范数: {np.linalg.norm(features):.4f}")
            return features.astype('float32')
            
        except Exception as e:
            print(f"文本编码失败: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros(512, dtype='float32')  # 返回零向量
    
    def encode_image(self, image_path: str) -> np.ndarray:
        """将图像编码为向量"""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            # 将特征转换为numpy数组并归一化
            features = image_features.squeeze().cpu().numpy()
            features = features / np.linalg.norm(features)
            return features.astype('float32')
        except Exception as e:
            print(f"图像编码失败 {image_path}: {e}")
            return np.zeros(512, dtype='float32')  # 返回零向量
    
    def add_image(self, image_path: str) -> bool:
        """添加图像到索引"""
        try:
            # 检查图像是否已存在于索引中
            if image_path in self.image_metadata:
                print(f"图像已存在于索引中: {image_path}")
                return True
            
            # 编码图像
            features = self.encode_image(image_path)
            features = features.reshape(1, -1)  # 调整形状为 (1, dimension)
            
            # 添加到FAISS索引
            self.index.add(features)
            
            # 保存元数据
            from services.image_processor_service import ImageFeatureExtractor
            processor = ImageFeatureExtractor()
            metadata = processor.extract_metadata(image_path)
            self.image_metadata[image_path] = metadata
            self.image_paths.append(image_path)
            
            print(f"图像已添加到索引: {image_path}")
            return True
        except Exception as e:
            print(f"添加图像失败 {image_path}: {e}")
            return False
    
    def remove_image(self, image_path: str) -> bool:
        """从索引中移除图像"""
        try:
            if image_path not in self.image_metadata:
                print(f"图像不在索引中: {image_path}")
                return False
            
            # 获取图像在索引中的位置
            idx = self.image_paths.index(image_path)
            
            # 从元数据和路径列表中移除
            del self.image_metadata[image_path]
            del self.image_paths[idx]
            
            # 注意：FAISS不直接支持删除向量，这里简化处理
            # 在实际应用中，可能需要重建索引或使用其他策略
            print(f"图像已从索引中移除: {image_path} (索引重建)")
            
            # 重建索引
            self.rebuild_index()
            
            return True
        except Exception as e:
            print(f"移除图像失败 {image_path}: {e}")
            return False
    
    def rebuild_index(self):
        """重建索引（在删除图像后）"""
        try:
            # 保存当前索引中的所有向量
            all_features = []
            for path in self.image_paths:
                features = self.encode_image(path)
                all_features.append(features)
            
            if all_features:
                # 堆叠所有特征向量
                all_features = np.stack(all_features)
                
                # 创建新索引
                dimension = all_features.shape[1]
                new_index = faiss.IndexFlatIP(dimension)
                new_index.add(all_features)
                
                # 替换当前索引
                self.index = new_index
            else:
                # 如果没有图像，创建空索引
                dimension = 512
                self.index = faiss.IndexFlatIP(dimension)
                
            print(f"索引重建完成，包含 {self.index.ntotal} 张图像")
        except Exception as e:
            print(f"重建索引失败: {e}")
    
    def search_by_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """根据文本搜索图像"""
        try:
            print(f"搜索查询: '{query}'")
            
            # 编码查询文本
            query_vector = self.encode_text(query)
            if query_vector is None or np.allclose(query_vector, 0):
                print("警告: 查询向量为空或全零")
                return []
                
            query_vector = query_vector.reshape(1, -1)  # 调整形状为 (1, dimension)
            print(f"查询向量维度: {query_vector.shape}, 范数: {np.linalg.norm(query_vector):.4f}")
            
            # 在索引中搜索
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            print(f"搜索完成，找到 {len(indices[0])} 个结果")
            
            # 构建结果
            results = []
            for i in range(len(indices[0])):
                idx = int(indices[0][i])  # 确保转换为Python int
                if idx < len(self.image_paths):
                    path = self.image_paths[idx]
                    similarity_score = float(scores[0][i])
                    print(f"结果 {i+1}: 相似度={similarity_score:.4f}, 路径={path}")
                    
                    metadata = self.image_metadata.get(path, {})
                    # 确保metadata中的所有数值都是JSON可序列化的
                    serializable_metadata = {}
                    for key, value in metadata.items():
                        if isinstance(value, (np.integer, np.int64)):
                            serializable_metadata[key] = int(value)
                        elif isinstance(value, (np.floating, np.float64)):
                            serializable_metadata[key] = float(value)
                        else:
                            serializable_metadata[key] = value
                    
                    results.append({
                        "id": idx,
                        "path": path,
                        "similarity": similarity_score,
                        "metadata": serializable_metadata
                    })
            
            return results
        except Exception as e:
            print(f"文本搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_by_image(self, query_image_path: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """以图搜图"""
        try:
            print(f"🔍 开始以图搜图: {query_image_path}")
            print(f"📊 当前索引包含 {self.index.ntotal} 张图像")
            print(f"📋 图像路径列表长度: {len(self.image_paths)}")
            
            # 编码查询图像
            query_vector = self.encode_image(query_image_path)
            if query_vector is None:
                print("❌ 查询图像编码失败")
                return []
                
            query_vector = query_vector.reshape(1, -1)  # 调整形状为 (1, dimension)
            print(f"🎯 查询向量维度: {query_vector.shape}, 范数: {np.linalg.norm(query_vector):.4f}")
            
            # 在索引中搜索
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            print(f"🔎 搜索完成，找到 {len(indices[0])} 个结果")
            
            # 打印前几个结果的详细信息
            print("📈 搜索结果详情:")
            for i in range(min(5, len(indices[0]))):
                idx = int(indices[0][i])
                score = float(scores[0][i])
                if idx < len(self.image_paths):
                    path = self.image_paths[idx]
                    print(f"  {i+1}. 索引:{idx}, 相似度:{score:.4f}, 路径:{path}")
            
            # 构建结果
            results = []
            for i in range(len(indices[0])):
                idx = int(indices[0][i])  # 确保转换为Python int
                if idx < len(self.image_paths):
                    path = self.image_paths[idx]
                    metadata = self.image_metadata.get(path, {})
                    # 确保metadata中的所有数值都是JSON可序列化的
                    serializable_metadata = {}
                    for key, value in metadata.items():
                        if isinstance(value, (np.integer, np.int64)):
                            serializable_metadata[key] = int(value)
                        elif isinstance(value, (np.floating, np.float64)):
                            serializable_metadata[key] = float(value)
                        else:
                            serializable_metadata[key] = value
                    
                    results.append({
                        "id": idx,
                        "path": path,
                        "similarity": float(scores[0][i]),
                        "metadata": serializable_metadata
                    })
            
            print(f"✅ 返回 {len(results)} 个搜索结果")
            return results
        except Exception as e:
            print(f"❌ 图像搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _get_model_path(self, model_name: str) -> str:
        """获取模型的实际路径"""
        model_mapping = {
            'clip-vit-base-patch32': "openai/clip-vit-base-patch32",
            'clip-vit-large-patch14': "openai/clip-vit-large-patch14", 
            'chinese-clip-vit-base-patch16': "OFA-Sys/chinese-clip-vit-base-patch16",
            'multilingual-clip-vit-base-patch32': "sentence-transformers/clip-ViT-B-32-multilingual-v1",
            'blip-base': "Salesforce/blip-image-captioning-base"
        }
        return model_mapping.get(model_name, "openai/clip-vit-base-patch32")
    
    def _save_model_info(self):
        """保存当前使用的模型信息"""
        try:
            model_info = {
                'model_name': self.current_model_name,
                'timestamp': time.time()
            }
            with open(self.model_info_path, 'wb') as f:
                pickle.dump(model_info, f)
        except Exception as e:
            print(f"保存模型信息失败: {e}")
    
    def _get_index_model_name(self) -> str:
        """获取索引使用的模型名称"""
        try:
            if os.path.exists(self.model_info_path):
                with open(self.model_info_path, 'rb') as f:
                    model_info = pickle.load(f)
                return model_info.get('model_name', '')
            return ''
        except Exception as e:
            print(f"读取模型信息失败: {e}")
            return ''

    def set_model(self, model_name: str):
        """设置使用的模型"""
        try:
            # 检查是否需要切换模型
            if model_name == self.current_model_name:
                print(f"模型已经是 {model_name}，无需切换")
                return
            
            # 获取模型路径
            model_path = self._get_model_path(model_name)
            
            print(f"正在切换模型: {self.current_model_name} -> {model_name}")
            
            # 加载新模型
            if model_name == 'blip-base':
                print("BLIP模型支持将在后续版本中添加")
                return
            elif model_name == 'chinese-clip-vit-base-patch16':
                # 使用Chinese CLIP专用的类和处理器
                self.clip_model = ChineseCLIPModel.from_pretrained(model_path)
                self.clip_processor = ChineseCLIPProcessor.from_pretrained(model_path)
            else:
                # 使用标准CLIP模型
                self.clip_model = CLIPModel.from_pretrained(model_path)
                self.clip_processor = CLIPProcessor.from_pretrained(model_path)
            
            # 确保模型处于评估模式
            self.clip_model.eval()
            
            # 更新当前模型名称
            old_model = self.current_model_name
            self.current_model_name = model_path
            
            print(f"✅ 成功切换模型: {model_name}")
            
            # 检查是否需要重建索引
            if self.index.ntotal > 0:
                print("⚠️  检测到现有索引，建议重新索引图片以确保搜索准确性")
                print("   可以调用 rebuild_index_with_new_model() 方法重建索引")
            
        except Exception as e:
            print(f"设置模型失败: {e}")
            # 恢复到原来的模型
            self.current_model_name = old_model if 'old_model' in locals() else self.current_model_name
    
    def rebuild_index_with_new_model(self):
        """使用新模型重建整个索引"""
        try:
            if not self.image_paths:
                print("没有图片需要重建索引")
                return
            
            print(f"开始使用模型 {self.current_model_name} 重建索引...")
            
            # 保存图片路径列表
            paths_to_rebuild = self.image_paths.copy()
            
            # 清空当前索引
            dimension = 512
            self.index = faiss.IndexFlatIP(dimension)
            self.image_paths = []
            
            # 重新编码所有图片
            success_count = 0
            for i, image_path in enumerate(paths_to_rebuild):
                try:
                    if os.path.exists(image_path):
                        # 重新编码并添加到索引
                        features = self.encode_image(image_path)
                        features = features.reshape(1, -1)
                        self.index.add(features)
                        self.image_paths.append(image_path)
                        success_count += 1
                        
                        if (i + 1) % 10 == 0:
                            print(f"已重建 {i + 1}/{len(paths_to_rebuild)} 张图片")
                    else:
                        print(f"图片不存在，跳过: {image_path}")
                        # 从元数据中移除
                        if image_path in self.image_metadata:
                            del self.image_metadata[image_path]
                            
                except Exception as e:
                    print(f"重建图片索引失败 {image_path}: {e}")
            
            print(f"✅ 索引重建完成！成功重建 {success_count} 张图片")
            
            # 保存新索引
            self.save_index()
            
        except Exception as e:
            print(f"重建索引失败: {e}")
    
    def rebuild_index_with_new_model_progress(self, task_id: str, processing_status: dict):
        """使用新模型重建整个索引（带进度更新）"""
        try:
            if not self.image_paths:
                print("没有图片需要重建索引")
                return
            
            print(f"开始使用模型 {self.current_model_name} 重建索引...")
            
            # 保存图片路径列表
            paths_to_rebuild = self.image_paths.copy()
            total_images = len(paths_to_rebuild)
            
            # 更新任务状态
            processing_status[task_id]["total"] = total_images
            
            # 清空当前索引
            dimension = 512
            self.index = faiss.IndexFlatIP(dimension)
            self.image_paths = []
            
            # 重新编码所有图片
            success_count = 0
            for i, image_path in enumerate(paths_to_rebuild):
                try:
                    if os.path.exists(image_path):
                        # 重新编码并添加到索引
                        features = self.encode_image(image_path)
                        features = features.reshape(1, -1)
                        self.index.add(features)
                        self.image_paths.append(image_path)
                        success_count += 1
                        
                        # 更新进度
                        processing_status[task_id]["processed"] = i + 1
                        processing_status[task_id]["progress"] = int((i + 1) / total_images * 100)
                        
                        if (i + 1) % 5 == 0:
                            print(f"已重建 {i + 1}/{total_images} 张图片")
                    else:
                        print(f"图片不存在，跳过: {image_path}")
                        # 从元数据中移除
                        if image_path in self.image_metadata:
                            del self.image_metadata[image_path]
                            
                except Exception as e:
                    print(f"重建图片索引失败 {image_path}: {e}")
            
            print(f"✅ 索引重建完成！成功重建 {success_count} 张图片")
            
            # 保存新索引
            self.save_index()
            
        except Exception as e:
            print(f"重建索引失败: {e}")