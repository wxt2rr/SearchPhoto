import os
import sys
from typing import List, Dict, Any, Tuple
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from models.image_processor import ImageProcessorInterface

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ImageFeatureExtractor(ImageProcessorInterface):
    """图像特征提取器实现"""
    
    def __init__(self):
        # 加载CLIP模型用于图像特征提取
        # 这使用了OpenAI的CLIP模型，它可以将图像和文本映射到同一特征空间
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # 用于文本编码的模型
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 将模型设置为评估模式
        self.clip_model.eval()
    
    def extract_features(self, image_path: str) -> List[float]:
        """
        提取图像特征向量
        使用CLIP模型提取图像的特征向量
        """
        try:
            # 加载图像
            image = Image.open(image_path).convert('RGB')
            
            # 预处理图像
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            # 使用模型提取特征
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            # 将特征向量转换为numpy数组并展平
            features = image_features.squeeze().cpu().numpy()
            
            # 转换为Python列表并返回
            return features.tolist()
        except Exception as e:
            print(f"Error extracting features for {image_path}: {e}")
            # 如果出错，返回一个零向量
            return [0.0] * 512  # CLIP base模型的特征维度是512
    
    def generate_thumbnail(self, image_path: str, size: Tuple[int, int] = (128, 128)) -> bytes:
        """生成缩略图"""
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')  # 确保是RGB模式
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 保存到字节流
                import io
                thumb_io = io.BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_io.seek(0)
                
                return thumb_io.getvalue()
        except Exception as e:
            print(f"Error generating thumbnail for {image_path}: {e}")
            raise e
    
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """提取图像元数据（如EXIF信息）"""
        try:
            with Image.open(image_path) as img:
                metadata = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": os.path.getsize(image_path)
                }
                
                # 提取EXIF数据（如果存在）
                exif_data = img._getexif()
                if exif_data:
                    # 简化的EXIF提取
                    from PIL.ExifTags import TAGS
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == "DateTimeOriginal":
                            metadata["DateTimeOriginal"] = value
                        elif tag == "GPSInfo":
                            # GPS信息处理（简化）
                            metadata["GPSInfo"] = str(value)
                
                return metadata
        except Exception as e:
            print(f"Error extracting metadata for {image_path}: {e}")
            # 返回基本文件信息
            return {
                "width": 0,
                "height": 0,
                "format": "",
                "mode": "",
                "size_bytes": os.path.getsize(image_path)
            }