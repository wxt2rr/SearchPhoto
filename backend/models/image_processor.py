from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np

class ImageProcessorInterface(ABC):
    """图像处理接口"""
    
    @abstractmethod
    def extract_features(self, image_path: str) -> List[float]:
        """提取图像特征向量"""
        pass
    
    @abstractmethod
    def generate_thumbnail(self, image_path: str, size: Tuple[int, int] = (128, 128)) -> bytes:
        """生成缩略图"""
        pass
    
    @abstractmethod
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """提取图像元数据（如EXIF信息）"""
        pass