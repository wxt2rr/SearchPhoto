#!/usr/bin/env python3
"""
最小化搜索测试
"""

import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
sys.path.append('.')

def test_minimal_search():
    """最小化搜索测试"""
    print("=== 最小化搜索测试 ===")
    
    try:
        from services.search_service import SemanticSearchService
        import numpy as np
        
        print("1. 创建搜索服务...")
        search_service = SemanticSearchService()
        
        print("2. 直接调用encode_text...")
        features = search_service.encode_text("小猫")
        print(f"   编码成功: {features.shape}")
        
        print("3. 手动执行搜索步骤...")
        query_vector = features.reshape(1, -1)
        print(f"   查询向量形状: {query_vector.shape}")
        
        print("4. 执行FAISS搜索...")
        scores, indices = search_service.index.search(query_vector, 3)
        print(f"   搜索成功: scores={scores.shape}, indices={indices.shape}")
        
        print("5. 构建结果...")
        results = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            if idx < len(search_service.image_paths):
                path = search_service.image_paths[idx]
                similarity_score = float(scores[0][i])
                results.append({
                    "id": idx,
                    "path": path,
                    "similarity": similarity_score,
                    "metadata": {}
                })
        
        print(f"6. 结果构建成功，共 {len(results)} 个结果:")
        for i, result in enumerate(results):
            print(f"   {i+1}. 相似度: {result['similarity']:.4f}, 文件: {os.path.basename(result['path'])}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_search()
    if success:
        print("\n✅ 最小化搜索测试成功")
    else:
        print("\n❌ 最小化搜索测试失败")