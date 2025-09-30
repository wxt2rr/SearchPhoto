#!/usr/bin/env python3
"""
测试修复版本的搜索服务
"""

import os
import sys
sys.path.append('.')

from services.search_service_fixed import SemanticSearchServiceFixed

def test_fixed_search_service():
    """测试修复版本的搜索服务"""
    print("=== 测试修复版本的搜索服务 ===")
    
    try:
        print("1. 创建搜索服务...")
        search_service = SemanticSearchServiceFixed()
        print(f"   索引包含 {search_service.index.ntotal} 张图像")
        
        print("2. 测试搜索功能...")
        test_queries = ["小猫", "cat", "人物", "person"]
        
        for query in test_queries:
            print(f"\n--- 搜索: '{query}' ---")
            results = search_service.search_by_text(query, top_k=3)
            
            if results:
                for i, result in enumerate(results):
                    filename = os.path.basename(result['path'])
                    print(f"  {i+1}. 相似度: {result['similarity']:.4f}, 文件: {filename}")
            else:
                print("  无搜索结果")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_search_service()
    if success:
        print("\n✅ 修复版本搜索服务测试成功！")
    else:
        print("\n❌ 修复版本仍有问题")