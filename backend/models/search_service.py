from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

class SearchServiceInterface(ABC):
    """搜索服务接口"""
    
    @abstractmethod
    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """根据文本搜索图像"""
        pass
    
    @abstractmethod
    def search_by_image(self, query_image_path: str) -> List[Dict[str, Any]]:
        """以图搜图"""
        pass
    
    @abstractmethod
    def add_image(self, image_path: str) -> bool:
        """添加图像到索引"""
        pass
    
    @abstractmethod
    def remove_image(self, image_id: str) -> bool:
        """从索引中移除图像"""
        pass