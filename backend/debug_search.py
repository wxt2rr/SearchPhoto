#!/usr/bin/env python3
"""
调试搜索问题
"""

import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'

import sys
sys.path.append('.')

def test_clip_directly():
    """直接测试CLIP模型"""
    print("=== 直接测试CLIP模型 ===")
    
    try:
        from transformers import CLIPProcessor, CLIPModel
        import torch
        import numpy as np
        
        print("1. 加载模型...")
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model.eval()
        
        print("2. 测试英文文本编码...")
        inputs = processor(text=["cat"], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        print(f"   英文编码成功: {text_features.shape}")
        
        print("3. 测试中文文本编码...")
        inputs = processor(text=["小猫"], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        print(f"   中文编码成功: {text_features.shape}")
        
        print("4. 测试FAISS搜索...")
        import faiss
        
        # 创建简单的测试索引
        dimension = 512
        index = faiss.IndexFlatIP(dimension)
        
        # 添加一些随机向量
        test_vectors = np.random.random((5, dimension)).astype('float32')
        # 归一化
        norms = np.linalg.norm(test_vectors, axis=1, keepdims=True)
        test_vectors = test_vectors / norms
        index.add(test_vectors)
        
        # 搜索
        query = test_vectors[0:1]
        scores, indices = index.search(query, 3)
        print(f"   FAISS搜索成功: {scores}, {indices}")
        
        return True
        
    except Exception as e:
        print(f"直接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_service_step_by_step():
    """逐步测试搜索服务"""
    print("\n=== 逐步测试搜索服务 ===")
    
    try:
        from services.search_service import SemanticSearchService
        
        print("1. 创建搜索服务...")
        search_service = SemanticSearchService()
        
        print("2. 检查索引状态...")
        print(f"   索引包含 {search_service.index.ntotal} 张图片")
        
        if search_service.index.ntotal == 0:
            print("   索引为空，无法测试搜索")
            return False
        
        print("3. 测试文本编码（简化版）...")
        # 直接使用CLIP模型，不通过search_service的encode_text方法
        from transformers import CLIPProcessor, CLIPModel
        import torch
        import numpy as np
        
        inputs = search_service.clip_processor(text=["cat"], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = search_service.clip_model.get_text_features(**inputs)
        
        features = text_features.squeeze().cpu().numpy()
        features = features / np.linalg.norm(features)
        print(f"   文本编码成功: {features.shape}")
        
        print("4. 测试FAISS搜索...")
        query_vector = features.reshape(1, -1)
        scores, indices = search_service.index.search(query_vector, 3)
        
        print(f"   搜索成功，找到 {len(indices[0])} 个结果")
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            if idx < len(search_service.image_paths):
                path = search_service.image_paths[idx]
                score = float(scores[0][i])
                print(f"     {i+1}. 相似度: {score:.4f}, 文件: {os.path.basename(path)}")
        
        return True
        
    except Exception as e:
        print(f"逐步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_clip_directly()
    success2 = test_search_service_step_by_step()
    
    if success1 and success2:
        print("\n✅ 所有测试通过，问题可能在search_by_text方法的复杂逻辑中")
    else:
        print("\n❌ 基础功能有问题")