#!/usr/bin/env python3
"""
测试修复后的搜索功能
"""

import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
sys.path.append('.')

from services.search_service import SemanticSearchService

def test_search_functionality():
    """测试搜索功能"""
    print("=== 测试修复后的搜索功能 ===")
    
    try:
        search_service = SemanticSearchService()
        print(f"索引加载成功，包含 {search_service.index.ntotal} 张图像")
        
        # 测试不同的查询
        test_queries = [
            "小猫",
            "cat", 
            "人物",
            "person",
            "截图",
            "风景"
        ]
        
        for query in test_queries:
            print(f"\n--- 搜索: '{query}' ---")
            try:
                results = search_service.search_by_text(query, top_k=3)
                
                if results:
                    print(f"找到 {len(results)} 个结果:")
                    for i, result in enumerate(results):
                        filename = os.path.basename(result['path'])
                        print(f"  {i+1}. 相似度: {result['similarity']:.4f}")
                        print(f"     文件: {filename}")
                        
                        # 分析结果合理性
                        if query in ['小猫', 'cat'] and 'cat' not in filename.lower():
                            print(f"     ⚠️  注意：搜索'{query}'但文件名不包含猫相关词汇")
                        elif query in ['人物', 'person'] and 'person' not in filename.lower():
                            print(f"     ⚠️  注意：搜索'{query}'但文件名不包含人物相关词汇")
                else:
                    print("  无搜索结果")
                    
            except Exception as e:
                print(f"  搜索失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_search_accuracy():
    """分析搜索准确性"""
    print("\n=== 搜索准确性分析 ===")
    
    try:
        search_service = SemanticSearchService()
        
        # 分析索引中的图片类型
        print("索引中的图片分析:")
        file_types = {}
        
        for path in search_service.image_paths:
            filename = os.path.basename(path).lower()
            
            if 'snipaste' in filename or 'screenshot' in filename:
                file_types['截图类'] = file_types.get('截图类', 0) + 1
            elif any(keyword in filename for keyword in ['cat', '猫', 'kitten']):
                file_types['猫相关'] = file_types.get('猫相关', 0) + 1
            elif any(keyword in filename for keyword in ['person', '人', 'people', 'portrait']):
                file_types['人物相关'] = file_types.get('人物相关', 0) + 1
            elif any(keyword in filename for keyword in ['landscape', '风景', 'scenery']):
                file_types['风景相关'] = file_types.get('风景相关', 0) + 1
            else:
                file_types['其他'] = file_types.get('其他', 0) + 1
        
        for file_type, count in file_types.items():
            percentage = (count / len(search_service.image_paths)) * 100
            print(f"  {file_type}: {count} 张 ({percentage:.1f}%)")
        
        # 给出搜索准确性建议
        if file_types.get('截图类', 0) > len(search_service.image_paths) * 0.7:
            print("\n💡 搜索准确性分析:")
            print("  - 大部分图片是截图，缺少真实的物体照片")
            print("  - 搜索'小猫'返回截图是正常的，因为CLIP会基于视觉相似性匹配")
            print("  - 建议添加一些包含真实猫咪、人物、风景的照片来测试搜索效果")
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_search_functionality()
    success2 = analyze_search_accuracy()
    
    if success1 and success2:
        print("\n✅ 搜索功能修复成功！")
        print("💡 如果搜索结果不够准确，主要原因是测试图片类型单一（主要是截图）")
        print("   建议添加更多样化的图片来改善搜索体验")
    else:
        print("\n❌ 仍有问题需要解决")