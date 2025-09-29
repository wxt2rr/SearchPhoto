import os
import sys
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
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
        
        # 加载文本编码模型
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 加载CLIP模型用于图像特征提取
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
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
                self.index = faiss.read_index(self.index_path)
                
                with open(self.metadata_path, 'rb') as f:
                    self.image_metadata = pickle.load(f)
                
                # 重建图像路径列表
                self.image_paths = list(self.image_metadata.keys())
                
                print(f"索引加载成功，包含 {self.index.ntotal} 张图像")
            else:
                print("未找到现有索引，将创建新的索引")
                # 创建新的FAISS索引（CLIP模型的特征维度是512）
                dimension = 512
                self.index = faiss.IndexFlatIP(dimension)  # 使用内积作为相似度度量
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
            
            print(f"索引已保存，包含 {self.index.ntotal} 张图像")
        except Exception as e:
            print(f"保存索引失败: {e}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """将文本编码为向量"""
        try:
            # 使用CLIP模型编码文本，确保与图像特征在同一空间
            inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
            
            with torch.no_grad():
                text_features = self.clip_model.get_text_features(**inputs)
            
            # 将特征转换为numpy数组并归一化
            features = text_features.squeeze().cpu().numpy()
            features = features / np.linalg.norm(features)
            return features.astype('float32')
        except Exception as e:
            print(f"文本编码失败: {e}")
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
            # 编码查询文本
            query_vector = self.encode_text(query)
            query_vector = query_vector.reshape(1, -1)  # 调整形状为 (1, dimension)
            
            # 在索引中搜索
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
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
            
            return results
        except Exception as e:
            print(f"文本搜索失败: {e}")
            return []
    
    def search_by_image(self, query_image_path: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """以图搜图"""
        try:
            # 编码查询图像
            query_vector = self.encode_image(query_image_path)
            query_vector = query_vector.reshape(1, -1)  # 调整形状为 (1, dimension)
            
            # 在索引中搜索
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
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
            
            return results
        except Exception as e:
            print(f"图像搜索失败: {e}")
            return []

    def set_model(self, model_name: str):
        """设置使用的模型"""
        try:
            # 根据模型名称加载相应的模型
            if model_name == 'clip-vit-base-patch32':
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            elif model_name == 'clip-vit-large-patch14':
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
            elif model_name == 'blip-base':
                # BLIP模型需要不同的处理方式
                # 这里可以添加对BLIP模型的支持
                print("BLIP模型支持将在后续版本中添加")
                return
            else:
                # 默认使用CLIP ViT-B/32
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # 确保模型处于评估模式
            self.clip_model.eval()
        except Exception as e:
            print(f"设置模型失败: {e}")