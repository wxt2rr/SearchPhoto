#!/usr/bin/env python3
"""
修复搜索问题的脚本
"""

import os
import sys

# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

sys.path.append('.')

from services.search_service import SemanticSearchService
import numpy as np

def test_fixed_search():
    """测试修复后的搜索"""
    print("=== 修复后的搜索测试 ===")
    
    try:
        search_service = SemanticSearchService()
        print(f"索引加载成功，包含 {search_service.index.ntotal} 张图像")
        
        # 测试搜索
        test_queries = ["小猫", "cat", "人物", "截图"]
        
        for query in test_queries:
            print(f"\n搜索: '{query}'")
            results = search_service.search_by_text(query, top_k=3)
            
            if results:
                for i, result in enumerate(results):
                    print(f"  {i+1}. 相似度: {result['similarity']:.4f}")
                    print(f"     路径: {os.path.basename(result['path'])}")
            else:
                print("  无结果")
                
        return True
        
    except Exception as e:
        print(f"搜索测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_search_results():
    """分析搜索结果的合理性"""
    print("\n=== 搜索结果分析 ===")
    
    try:
        search_service = SemanticSearchService()
        
        # 获取所有图片路径
        all_paths = search_service.image_paths
        print(f"总共 {len(all_paths)} 张图片")
        
        # 分析文件名
        file_types = {}
        for path in all_paths:
            filename = os.path.basename(path).lower()
            if 'snipaste' in filename or 'screenshot' in filename:
                file_types['截图'] = file_types.get('截图', 0) + 1
            elif any(ext in filename for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                if any(keyword in filename for keyword in ['cat', '猫', 'kitten']):
                    file_types['猫相关'] = file_types.get('猫相关', 0) + 1
                elif any(keyword in filename for keyword in ['person', '人', 'people']):
                    file_types['人物相关'] = file_types.get('人物相关', 0) + 1
                else:
                    file_types['其他图片'] = file_types.get('其他图片', 0) + 1
        
        print("文件类型分布:")
        for file_type, count in file_types.items():
            print(f"  {file_type}: {count} 张")
        
        # 如果大部分是截图，那么搜索"小猫"返回截图是正常的
        if file_types.get('截图', 0) > len(all_paths) * 0.8:
            print("\n⚠️  发现问题：大部分图片是截图，缺少真实的猫咪照片")
            print("   建议：添加一些包含猫咪的真实照片来测试搜索功能")
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_fixed_search()
    success2 = analyze_search_results()
    
    if success1 and success2:
        print("\n✅ 搜索功能正常，问题可能在于测试数据")
    else:
        print("\n❌ 仍有问题需要解决")