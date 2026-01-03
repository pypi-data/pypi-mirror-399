"""
Gov Stats MCP Server 测试文件
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query import GovStatsQueryEngine
from constants import INDICATOR_DESCRIPTIONS, REGION_CODES, CITY_CODES, DATABASE_CODES


def test_constants():
    """测试常量定义"""
    print("📚 测试常量定义...")
    
    print(f"   指标代码数量: {len(INDICATOR_DESCRIPTIONS)}")
    print(f"   地区代码数量: {len(REGION_CODES)}")
    print(f"   城市代码数量: {len(CITY_CODES)}")
    print(f"   数据库代码数量: {len(DATABASE_CODES)}")
    
    # 显示部分示例
    print("\n   示例指标代码:")
    for i, (code, desc) in enumerate(list(INDICATOR_DESCRIPTIONS.items())[:5]):
        print(f"     {code}: {desc}")
    
    print("\n   示例地区代码:")
    for i, (code, name) in enumerate(list(REGION_CODES.items())[:5]):
        print(f"     {code}: {name}")
    
    print("\n   示例城市代码:")
    for i, (code, name) in enumerate(list(CITY_CODES.items())[:5]):
        print(f"     {code}: {name}")
    
    print("\n   数据库代码:")
    for code, desc in DATABASE_CODES.items():
        print(f"     {code}: {desc}")
    
    print("\n   ✅ 常量定义测试完成")


def test_query_engine():
    """测试查询引擎"""
    print("\n🔍 测试国家统计局数据查询引擎...")
    
    engine = GovStatsQueryEngine()
    
    # 测试数据
    test_queries = [
        {
            "zbcode": "A010101",
            "datestr": "202401",
            "dbcode": "hgyd",
            "description": "全国居民消费价格分类指数(宏观月度)"
        },
        {
            "zbcode": "A0D0101",
            "datestr": "202401",
            "dbcode": "hgyd",
            "description": "货币供应量(M2)"
        },
        {
            "zbcode": "A010101",
            "datestr": "202401",
            "dbcode": "fsyd",
            "regcode": "110000",
            "description": "北京市居民消费价格指数(分省月度)"
        },
        {
            "zbcode": "A010101",
            "datestr": "202401",
            "dbcode": "csyd",
            "regcode": "370200",
            "description": "青岛市居民消费价格指数(城市月度)"
        }
    ]
    
    for test in test_queries:
        try:
            print(f"\n📊 测试查询: {test['description']}")
            print(f"   指标代码: {test['zbcode']}")
            print(f"   查询日期: {test['datestr']}")
            print(f"   数据库: {test['dbcode']}")
            if 'regcode' in test:
                print(f"   地区代码: {test['regcode']}")
            
            result = engine.query_stats_data(
                zbcode=test['zbcode'],
                datestr=test['datestr'],
                dbcode=test['dbcode'],
                regcode=test.get('regcode')
            )
            
            print(f"   查询结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            print("   ✅ 查询成功")
            
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
    
    print("\n   ✅ 查询引擎测试完成")


def test_batch_query():
    """测试批量查询"""
    print("\n📦 测试批量查询...")
    
    engine = GovStatsQueryEngine()
    
    zbcodes = ["A010101", "A010801", "A0D0101"]
    datestr = "202401"
    
    print(f"   批量查询指标: {zbcodes}")
    print(f"   查询日期: {datestr}")
    
    results = []
    for zbcode in zbcodes:
        try:
            result = engine.query_stats_data(
                zbcode=zbcode,
                datestr=datestr,
                dbcode="hgyd"
            )
            results.append({
                "zbcode": zbcode,
                "description": INDICATOR_DESCRIPTIONS.get(zbcode, "未知指标"),
                "success": True,
                "data": result
            })
            print(f"   ✅ {zbcode}: 查询成功")
        except Exception as e:
            results.append({
                "zbcode": zbcode,
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ {zbcode}: 查询失败 - {e}")
    
    print(f"\n   批量查询完成: {len([r for r in results if r['success']])}/{len(zbcodes)} 成功")
    print("\n   ✅ 批量查询测试完成")


def main():
    """主测试函数"""
    print("🚀 开始 Gov Stats MCP Server 测试")
    print("=" * 60)
    
    test_constants()
    test_query_engine()
    test_batch_query()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成")


if __name__ == "__main__":
    main()
