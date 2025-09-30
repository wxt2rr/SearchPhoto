#!/usr/bin/env python3
"""
测试模型切换功能
"""

import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
sys.path.append('.')

from services.search_service import SemanticSearchService

def test_model_switch():
    """测试模型切换功能"""
    print("=== 模型切换测试 ===")
    
    try:
        search_service = SemanticSearchService()
        print(f"初始模型: {search_service.current_model_name}")
        print(f"索引中图片数量: {search_service.index.ntotal}")
        
        # 测试搜索"小猫"
        print("\n--- 使用默认模型搜索 ---")
        results = search_service.search_by_text("小猫", top_k=3)
        print(f"搜索结果数量: {len(results)}")
        for i, result in enumerate(results):
            print(f"  {i+1}. 相似度: {result['similarity']:.4f}, 文件: {os.path.basename(result['path'])}")
        
        # 切换到中文CLIP模型
        print("\n--- 切换到中文CLIP模型 ---")
        search_service.set_model('chinese-clip-vit-base-patch16')
        
        # 重建索引
        if search_service.index.ntotal > 0:
            print("重建索引以匹配新模型...")
            search_service.rebuild_index_with_new_model()
        
        # 再次测试搜索
        print("\n--- 使用中文CLIP模型搜索 ---")
        results = search_service.search_by_text("小猫", top_k=3)
        print(f"搜索结果数量: {len(results)}")
        for i, result in enumerate(results):
            print(f"  {i+1}. 相似度: {result['similarity']:.4f}, 文件: {os.path.basename(result['path'])}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_switch()
    if success:
        print("\n✅ 模型切换测试完成")
    else:
        print("\n❌ 模型切换测试失败")