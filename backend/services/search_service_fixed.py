import os
import sys
import pickle
import faiss
import numpy as np
import time
from typing import List, Dict, Any
import torch
from PIL import Image

# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SemanticSearchServiceFixed:
    """修复版本的语义搜索服务"""
    
    def __init__(self, index_path: str = "image_index.faiss", metadata_path: str = "image_metadata.pkl"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model_info_path = "model_info.pkl"
        
        # 当前使用的模型名称
        self.current_model_name = "openai/clip-vit-base-patch32"
        
        # 延迟加载模型，避免初始化时的问题
        self.clip_model = None
        self.clip_processor = None
        
        # 初始化FAISS索引
        self.index = None
        self.image_metadata = {}
        self.image_paths = []
        
        # 加载索引
        self.load_index()
        
        # 只在需要时加载模型
        self._model_loaded = False
    
    def _ensure_model_loaded(self):
        """确保模型已加载"""
        if not self._model_loaded:
            try:
                print(f"正在加载模型: {self.current_model_name}")
                from transformers import CLIPProcessor, CLIPModel
                
                self.clip_model = CLIPModel.from_pretrained(self.current_model_name)
                self.clip_processor = CLIPProcessor.from_pretrained(self.current_model_name)
                self.clip_model.eval()
                
                # 设置为CPU模式，避免GPU相关问题
                self.clip_model = self.clip_model.cpu()
                
                self._model_loaded = True
                print(f"✅ 模型加载成功: {self.current_model_name}")
                
            except Exception as e:
                print(f"❌ 模型加载失败: {e}")
                raise e
    
    def load_index(self):
        """加载已保存的索引"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                
                with open(self.metadata_path, 'rb') as f:
                    self.image_metadata = pickle.load(f)
                
                self.image_paths = list(self.image_metadata.keys())
                print(f"索引加载成功，包含 {self.index.ntotal} 张图像")
            else:
                print("未找到现有索引，将创建新的索引")
                dimension = 512
                self.index = faiss.IndexFlatIP(dimension)
        except Exception as e:
            print(f"加载索引失败: {e}")
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
        """将文本编码为向量 - 使用更安全的方法"""
        try:
            self._ensure_model_loaded()
            print(f"编码文本: '{text}'")
            
            # 对中文进行简单翻译
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                translation_map = {
                    '小猫': 'cat',
                    '猫': 'cat',
                    '狗': 'dog',
                    '人物': 'person',
                    '风景': 'landscape',
                    '建筑': 'building',
                    '食物': 'food'
                }
                if text in translation_map:
                    text = translation_map[text]
                    print(f"翻译为: '{text}'")
            
            # 使用更安全的编码方式
            try:
                # 方法1：使用tokenizer手动处理
                tokenizer = self.clip_processor.tokenizer
                inputs = tokenizer([text], padding=True, return_tensors="pt")
                
                with torch.no_grad():
                    # 确保在CPU上运行
                    inputs = {k: v.cpu() for k, v in inputs.items()}
                    text_features = self.clip_model.get_text_features(**inputs)
                    text_features = text_features.cpu()
                
            except Exception as e1:
                print(f"方法1失败，尝试方法2: {e1}")
                # 方法2：使用processor但限制长度
                text = text[:77]  # CLIP的最大长度限制
                inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True)
                
                with torch.no_grad():
                    inputs = {k: v.cpu() for k, v in inputs.items()}
                    text_features = self.clip_model.get_text_features(**inputs)
                    text_features = text_features.cpu()
            
            # 转换为numpy并归一化
            features = text_features.squeeze().cpu().numpy()
            features = features / np.linalg.norm(features)
            
            print(f"文本编码完成，特征维度: {features.shape}")
            return features.astype('float32')
            
        except Exception as e:
            print(f"文本编码失败: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros(512, dtype='float32')
    
    def encode_image(self, image_path: str) -> np.ndarray:
        """将图像编码为向量"""
        try:
            self._ensure_model_loaded()
            
            image = Image.open(image_path).convert('RGB')
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                inputs = {k: v.cpu() for k, v in inputs.items()}
                image_features = self.clip_model.get_image_features(**inputs)
                image_features = image_features.cpu()
            
            features = image_features.squeeze().cpu().numpy()
            features = features / np.linalg.norm(features)
            return features.astype('float32')
        except Exception as e:
            print(f"图像编码失败 {image_path}: {e}")
            return np.zeros(512, dtype='float32')
    
    def search_by_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """根据文本搜索图像"""
        try:
            print(f"搜索查询: '{query}'")
            
            # 编码查询文本
            query_vector = self.encode_text(query)
            if np.allclose(query_vector, 0):
                print("警告: 查询向量为零")
                return []
            
            query_vector = query_vector.reshape(1, -1)
            
            # 在索引中搜索
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            # 构建结果
            results = []
            for i in range(len(indices[0])):
                idx = int(indices[0][i])
                if idx < len(self.image_paths):
                    path = self.image_paths[idx]
                    similarity_score = float(scores[0][i])
                    
                    metadata = self.image_metadata.get(path, {})
                    # 确保metadata可序列化
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
            
            print(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            print(f"文本搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def add_image(self, image_path: str) -> bool:
        """添加图像到索引"""
        try:
            if image_path in self.image_metadata:
                print(f"图像已存在于索引中: {image_path}")
                return True
            
            features = self.encode_image(image_path)
            features = features.reshape(1, -1)
            
            self.index.add(features)
            
            # 简化的元数据
            self.image_metadata[image_path] = {
                'path': image_path,
                'filename': os.path.basename(image_path),
                'size': os.path.getsize(image_path) if os.path.exists(image_path) else 0,
                'timestamp': time.time()
            }
            self.image_paths.append(image_path)
            
            print(f"图像已添加到索引: {image_path}")
            return True
        except Exception as e:
            print(f"添加图像失败 {image_path}: {e}")
            return False