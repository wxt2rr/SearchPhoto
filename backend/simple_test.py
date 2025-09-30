#!/usr/bin/env python3
"""
简单的搜索测试脚本
"""

import sys
import os
sys.path.append('.')

def test_basic_functionality():
    """测试基本功能"""
    print("=== 基本功能测试 ===")
    
    try:
        # 测试模型加载
        print("1. 测试CLIP模型加载...")
        from transformers import CLIPProcessor, CLIPModel
        import torch
        
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model.eval()
        print("   ✓ CLIP模型加载成功")
        
        # 测试文本编码
        print("2. 测试文本编码...")
        inputs = processor(text=["cat", "小猫"], return_tensors="pt", padding=True)
        
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        
        print(f"   ✓ 文本编码成功，特征形状: {text_features.shape}")
        
        # 测试相似度计算
        print("3. 测试相似度计算...")
        import numpy as np
        
        # 归一化特征
        features_norm = text_features / text_features.norm(dim=-1, keepdim=True)
        
        # 计算相似度
        similarity = torch.mm(features_norm, features_norm.t())
        print(f"   ✓ 相似度矩阵: {similarity}")
        
        # 检查"cat"和"小猫"的相似度
        cat_xiaomao_sim = similarity[0, 1].item()
        print(f"   'cat' 和 '小猫' 的相似度: {cat_xiaomao_sim:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_faiss_index():
    """测试FAISS索引"""
    print("\n=== FAISS索引测试 ===")
    
    try:
        import faiss
        import numpy as np
        
        # 创建测试数据
        dimension = 512
        n_vectors = 5
        test_vectors = np.random.random((n_vectors, dimension)).astype('float32')
        
        # 归一化向量
        norms = np.linalg.norm(test_vectors, axis=1, keepdims=True)
        test_vectors = test_vectors / norms
        
        print(f"1. 创建测试向量: {test_vectors.shape}")
        
        # 创建索引
        index = faiss.IndexFlatIP(dimension)
        index.add(test_vectors)
        
        print(f"2. 创建FAISS索引，包含 {index.ntotal} 个向量")
        
        # 测试搜索
        query_vector = test_vectors[0:1]  # 使用第一个向量作为查询
        scores, indices = index.search(query_vector, 3)
        
        print(f"3. 搜索结果:")
        print(f"   得分: {scores[0]}")
        print(f"   索引: {indices[0]}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ FAISS测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_existing_index():
    """分析现有索引"""
    print("\n=== 现有索引分析 ===")
    
    try:
        import faiss
        import pickle
        
        index_path = "image_index.faiss"
        metadata_path = "image_metadata.pkl"
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            # 加载索引
            index = faiss.read_index(index_path)
            print(f"1. 索引包含 {index.ntotal} 个向量")
            
            # 加载元数据
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            print(f"2. 元数据包含 {len(metadata)} 个条目")
            
            # 显示前几个图片路径
            paths = list(metadata.keys())[:5]
            print("3. 图片路径示例:")
            for i, path in enumerate(paths):
                exists = "✓" if os.path.exists(path) else "✗"
                print(f"   {i+1}. {exists} {path}")
            
            return True
        else:
            print("   索引文件不存在")
            return False
            
    except Exception as e:
        print(f"   ✗ 索引分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_basic_functionality()
    success2 = test_faiss_index()
    success3 = analyze_existing_index()
    
    if all([success1, success2, success3]):
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败，需要进一步调试")