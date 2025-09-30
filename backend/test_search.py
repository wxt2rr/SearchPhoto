#!/usr/bin/env python3
"""
搜索功能测试脚本
用于分析和调试搜索不准确的问题
"""

import sys
import os
sys.path.append('.')

from services.search_service import SemanticSearchService
import numpy as np

def test_search_accuracy():
    """测试搜索准确性"""
    search_service = SemanticSearchService()
    
    print("=== 搜索准确性测试 ===")
    print(f"索引中图片数量: {search_service.index.ntotal}")
    print(f"图片路径示例: {search_service.image_paths[:3]}")
    
    # 测试不同的查询
    test_queries = [
        "小猫",
        "cat", 
        "kitten",
        "人物",
        "person",
        "截图",
        "screenshot",
        "风景",
        "landscape"
    ]
    
    for query in test_queries:
        print(f"\n=== 搜索: '{query}' ===")
        try:
            results = search_service.search_by_text(query, top_k=3)
            if results:
                for i, result in enumerate(results):
                    print(f"{i+1}. 相似度: {result['similarity']:.4f}")
                    print(f"   路径: {result['path']}")
                    # 分析文件名，看是否包含相关关键词
                    filename = os.path.basename(result['path']).lower()
                    print(f"   文件名: {filename}")
            else:
                print("   无结果")
        except Exception as e:
            print(f"   搜索失败: {e}")
    
    # 测试特征向量质量
    print(f"\n=== 特征向量分析 ===")
    try:
        # 编码几个测试文本
        cat_vector = search_service.encode_text("小猫")
        cat_en_vector = search_service.encode_text("cat")
        person_vector = search_service.encode_text("人物")
        
        print(f"'小猫' 向量范数: {np.linalg.norm(cat_vector):.4f}")
        print(f"'cat' 向量范数: {np.linalg.norm(cat_en_vector):.4f}")
        print(f"'人物' 向量范数: {np.linalg.norm(person_vector):.4f}")
        
        # 计算向量间相似度
        cat_similarity = np.dot(cat_vector, cat_en_vector)
        print(f"'小猫' 和 'cat' 的相似度: {cat_similarity:.4f}")
        
    except Exception as e:
        print(f"特征向量分析失败: {e}")

def analyze_image_content():
    """分析索引中图片的内容"""
    search_service = SemanticSearchService()
    
    print("\n=== 图片内容分析 ===")
    
    # 随机选择几张图片进行分析
    sample_paths = search_service.image_paths[:5]
    
    for path in sample_paths:
        print(f"\n分析图片: {path}")
        filename = os.path.basename(path)
        print(f"文件名: {filename}")
        
        # 检查文件是否存在
        if os.path.exists(path):
            print("文件存在")
            # 可以添加更多分析，比如图片尺寸、类型等
        else:
            print("文件不存在!")

if __name__ == "__main__":
    test_search_accuracy()
    analyze_image_content()