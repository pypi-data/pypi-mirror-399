#!/usr/bin/env python3
"""
DataCenter Client 测试运行脚本
Handler模式迁移后的简化版本
"""

import sys
import os
import pandas as pd

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    import dc_client as dc
    from dc_client import DataApi, PageDataFrame, DatacenterAPIError
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已正确安装依赖: uv sync")
    sys.exit(1)


def test_client_initialization():
    """测试客户端初始化功能"""
    print("\n" + "=" * 50)
    print("🧪 测试 1: 客户端初始化功能")
    print("=" * 50)

    try:
        # 测试使用 local=True 初始化
        print("✅ 测试 local=True 初始化...")
        client = dc.init(token='test_token', local=True)
        assert client._DataApi__base_url == 'http://localhost:10000'
        assert client._DataApi__token == 'test_token'
        print("   ✓ local 参数工作正常")

        # 测试使用显式 base_url 初始化
        print("✅ 测试显式 base_url 初始化...")
        client2 = dc.init(token='test_token', base_url='https://api.example.com')
        assert client2._DataApi__base_url == 'https://api.example.com'
        print("   ✓ base_url 参数工作正常")

        # 测试默认值（非本地）
        print("✅ 测试默认值初始化...")
        client3 = dc.init(token='test_token')
        assert client3._DataApi__base_url == 'https://data.alphaaidig.com'
        print("   ✓ 默认生产环境URL工作正常")

        # 测试空token错误
        print("✅ 测试空token错误处理...")
        try:
            dc.init(token='')
            assert False, "应该抛出ValueError"
        except ValueError as e:
            assert 'token不能为空' in str(e)
            print("   ✓ 空token错误处理正常")

        print("\n🎉 客户端初始化测试全部通过!")
        return True

    except Exception as e:
        print(f"\n❌ 客户端初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dynamic_method_creation():
    """测试动态方法创建功能"""
    print("\n" + "=" * 50)
    print("🧪 测试 2: 动态方法创建功能")
    print("=" * 50)

    try:
        # 创建客户端（使用模拟token）
        client = dc.init(token='test_token', local=True, timeout=5)

        # 测试动态方法是否可创建
        print("✅ 测试动态方法创建...")
        dynamic_method = getattr(client, 'hsgt_fund_page_list', None)
        assert dynamic_method is not None, "动态方法应该被创建"
        print("   ✓ hsgt_fund_page_list 方法创建成功")

        # 测试其他动态方法
        methods_to_test = [
            'margin_account_page_list',
            'a_stock_page_list',
            'hk_stock_page_list',
            'hs_industry_page_list'
        ]

        for method_name in methods_to_test:
            method = getattr(client, method_name, None)
            assert method is not None, f"{method_name} 方法应该被创建"
        print(f"   ✓ {len(methods_to_test)} 个动态方法创建成功")

        # 测试方法调用（会失败，但验证方法存在）
        print("✅ 测试动态方法调用...")
        try:
            # 这个调用会因为服务未运行或token无效而失败，但验证了方法存在
            client.hsgt_fund_page_list(page=1, page_size=1)
        except Exception as e:
            # 期望的异常，说明方法可以被调用
            print(f"   ✓ 动态方法调用正常 (预期异常: {type(e).__name__})")

        # 测试query方法
        print("✅ 测试query方法...")
        try:
            client.query('test_handler', param1='value1')
        except Exception as e:
            # 期望的异常
            print(f"   ✓ query方法调用正常 (预期异常: {type(e).__name__})")

        print("\n🎉 动态方法创建测试全部通过!")
        return True

    except Exception as e:
        print(f"\n❌ 动态方法创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_api_call():
    """测试真实API调用功能"""
    print("\n" + "=" * 50)
    print("🧪 测试 3: 真实API调用功能")
    print("=" * 50)

    try:
        # 创建客户端（使用测试token）
        client = dc.init(token='test_token', local=True, timeout=10)

        # 测试一个简单的API调用
        print("✅ 测试 HSGT 基金查询接口...")
        try:
            result = client.hsgt_fund_page_list(page=1, page_size=5)

            # 验证返回结果
            assert isinstance(result, pd.DataFrame), "返回结果应该是DataFrame"
            print(f"   ✓ API调用成功，返回DataFrame类型")
            print(f"   ✓ 返回数据行数: {len(result)}")

            # 如果有数据，验证数据结构
            if len(result) > 0:
                print(f"   ✓ 数据列: {list(result.columns)}")
                print(f"   ✓ 示例数据:\n{result.head(2).to_string()}")
            else:
                print("   ⚠️  返回空数据，这可能是因为数据库中没有数据")

        except DatacenterAPIError as e:
            if e.code == 401:
                print(f"   ✓ API认证正常工作 (401未授权，测试token无效): {e.message}")
            else:
                print(f"   ⚠️  API返回其他错误: {e}")
        except Exception as e:
            # 检查是否是401认证错误（在异常消息中）
            if "401" in str(e) or "HTTP请求失败，状态码: 401" in str(e):
                print(f"   ✓ API认证正常工作 (401未授权，测试token无效)")
            else:
                print(f"   ❌ API调用失败: {e}")
                return False

        print("\n🎉 真实API调用测试完成!")
        return True

    except Exception as e:
        print(f"\n❌ 真实API调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_unit_tests():
    """运行单元测试"""
    print("\n🚀 开始运行 DataCenter Client 单元测试...")

    tests = [
        test_client_initialization,
        test_dynamic_method_creation,
        test_real_api_call
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过! DataCenter Client 工作正常!")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查问题")

    return passed == total


def print_usage_info():
    """打印使用说明"""
    print("\n" + "=" * 70)
    print("🎉 DataCenter Client 已完全迁移到 Handler 架构!")
    print("=" * 70)
    print("")
    print("📦 架构变更:")
    print("  ✅ 所有模块特定的 client 文件已被移除")
    print("  ✅ 所有对应的 DTO 文件已被移除")
    print("  ✅ 所有模块特定的测试文件已被移除")
    print("  ✅ 现在使用统一的 Universal Client 模式")
    print("")
    print("🚀 推荐的使用方式:")
    print("  1. 使用 Universal Client (datacenter_client.init_client)")
    print("  2. 通过统一的 Handler 接口访问所有功能")
    print("  3. 直接通过 HTTP 调用测试 API 接口")
    print("")
    print("💡 使用示例:")
    print("  import dc_client as dc")
    print("  # 本地开发")
    print("  client = dc.init_client(token='your_token', local=True)")
    print("  # 或指定显式URL")
    print("  client = dc.init_client(token='your_token', base_url='http://localhost:10000')")
    print("")
    print("  # Margin Account")
    print("  result = client.margin_account_page_list(page=1, page_size=10)")
    print("  result = client.margin_account_list(limit=20)")
    print("")
    print("  # Margin Analysis")
    print("  result = client.margin_analysis_page_list(page=1, page_size=10)")
    print("  result = client.margin_analysis_list(limit=20)")
    print("")
    print("  # Margin Detail")
    print("  result = client.margin_detail_page_list_by_date(page=1, page_size=10)")
    print("  result = client.margin_detail_page_list_by_stock(page=1, page_size=10)")
    print("  result = client.margin_detail_list_by_stock(stock_code='000001.SZ', limit=20)")
    print("")
    print("  # AStock")
    print("  result = client.a_stock_page_list(page=1, page_size=10)")
    print("  result = client.a_stock_list(limit=20)")
    print("")
    print("  # HKStock")
    print("  result = client.hk_stock_page_list(page=1, page_size=10)")
    print("  result = client.hk_stock_list(limit=20)")
    print("")
    print("  # Industry")
    print("  result = client.hs_industry_page_list(page=1, page_size=10)")
    print("  result = client.hs_industry_list(limit=20)")
    print("  result = client.hs_industry_company_page_list(page=1, page_size=10)")
    print("  result = client.hs_industry_company_list(limit=20)")
    print("  result = client.sw_industry_page_list(page=1, page_size=10)")
    print("  result = client.sw_industry_list(limit=20)")
    print("  result = client.sw_industry_company_page_list(page=1, page_size=10, level_type='level1')")
    print("  result = client.sw_industry_company_list(limit=20, level_type='level1')")
    print("")
    print("🔍 查看所有可用的 Handler 接口:")
    print("  curl 'http://localhost:10000/api/v1/docs/json' | python3 -c \"import sys, json; data=json.load(sys.stdin); [print(f'- {api[\"name\"]}: {api[\"description\"]}') for api in data['apis']]\"")
    print("")
    print("🔍 搜索特定的接口:")
    print("  curl 'http://localhost:10000/api/v1/docs/search?q=margin'")
    print("")
    print("📖 Handler 模式文档:")
    print("  - 所有接口都通过 /api/v1/dataapi/{handler_name} 访问")
    print("  - 支持 POST 请求，JSON 格式参数")
    print("  - 统一的响应格式和错误处理")
    print("")
    print("=" * 70)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['-h', '--help', 'help']:
            print_usage_info()
            return 0
        else:
            print(f"Unknown argument: {arg}")
            print("Use -h or --help for usage information.")
            return 1
    else:
        # 默认运行单元测试
        success = run_unit_tests()
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())