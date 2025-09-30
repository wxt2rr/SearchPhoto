#!/usr/bin/env python3
"""
基础初始化测试
"""

import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
sys.path.append('.')

def test_step_by_step_init():
    """逐步测试初始化过程"""
    print("=== 逐步测试初始化过程 ===")
    
    try:
        print("1. 导入基础模块...")
        import pickle
        import faiss
        import numpy as np
        import time
        from typing import List, Dict, Any
        print("   ✓ 基础模块导入成功")
        
        print("2. 导入transformers...")
        from transformers import CLIPProcessor, CLIPModel
        import torch
        print("   ✓ transformers导入成功")
        
        print("3. 导入sentence_transformers...")
        from sentence_transformers import SentenceTransformer
        print("   ✓ sentence_transformers导入成功")
        
        print("4. 加载SentenceTransformer模型...")
        text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("   ✓ SentenceTransformer模型加载成功")
        
        print("5. 加载CLIP模型...")
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model.eval()
        print("   ✓ CLIP模型加载成功")
        
        print("6. 检查索引文件...")
        index_path = "image_index.faiss"
        metadata_path = "image_metadata.pkl"
        
        if os.path.exists(index_path):
            print(f"   ✓ 找到索引文件: {index_path}")
            index = faiss.read_index(index_path)
            print(f"   ✓ 索引加载成功，包含 {index.ntotal} 个向量")
        else:
            print(f"   ! 索引文件不存在: {index_path}")
            
        if os.path.exists(metadata_path):
            print(f"   ✓ 找到元数据文件: {metadata_path}")
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            print(f"   ✓ 元数据加载成功，包含 {len(metadata)} 个条目")
        else:
            print(f"   ! 元数据文件不存在: {metadata_path}")
        
        print("7. 测试简单的文本编码...")
        inputs = clip_processor(text=["test"], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
        features = text_features.squeeze().cpu().numpy()
        print(f"   ✓ 文本编码成功: {features.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 步骤失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_by_step_init()
    if success:
        print("\n✅ 所有初始化步骤成功")
    else:
        print("\n❌ 初始化过程中出现问题")