# DataCenter Client 使用指南

## 1. 🚀 安装

```bash
pip install datacenter_client
```

## 2. 🔑 认证设置

### 获取API Token
1. 联系管理员申请API Token
2. 或者访问数据管理后台获取访问权限

### 初始化客户端
```python
import datacenter_client as dc

# 基础初始化
client = dc.init(
    token='your_api_token_here'
)

# 使用环境变量
import os
client = dc.init(token=os.getenv('DATACENTER_API_TOKEN'))
```

## 3. 🔍 查找需要的接口

### 方法一：查看完整API列表
```python
import requests

# 获取所有API
response = requests.get('http://data.alphaaidig.com/api/v1/docs/json')
if response.status_code == 200:
    docs = response.json()
    print(f"总共有 {docs['total_count']} 个API")
    for api in docs['apis']:
        print(f"- {api['name']}: {api['description']}")
```

### 方法二：搜索特定功能
```python
# 搜索融资融券相关接口
response = requests.get('http://data.alphaaidig.com/api/v1/docs/search?q=margin')
if response.status_code == 200:
    results = response.json()
    for api in results['results']:
        print(f"- {api['name']}: {api['description']}")
```

### 方法三：按类别查看
```python
# 获取API分类
response = requests.get('http://data.alphaaidig.com/api/v1/docs/categories')
if response.status_code == 200:
    categories = response.json()
    print(f"API分类: {categories['categories']}")
```

## 4. 📋 访问接口

### 基本调用方式
```python
# 方式一：通过动态方法调用
result = client.hsgt_fund_page_list(page=1, page_size=20)

# 方式二：通过通用query方法
result = client.query('hsgt_fund_page_list', page=1, page_size=20)

# 方式三：指定返回字段
result = client.hsgt_fund_page_list(
    page=1,
    page_size=10,
    fields='trade_date,stock_code,stock_name,hold_market_cap'
)
```

### 常用接口示例
```python
# 沪深港通数据
df = client.hsgt_fund_page_list(page=1, page_size=20)
df = client.hsgt_north_fundxx()
df = client.hsgt_south_fundxx()

# A股数据
df = client.a_stock_page_list(page=1, page_size=20)
df = client.a_stock_list(limit=50)

# 港股数据
df = client.hk_stock_page_list(page=1, page_size=20)
df = client.hk_stock_list(limit=50)

# 行业数据
df = client.hs_industry_page_list(page=1, page_size=20)
df = client.hs_industry_company_page_list(page=1, page_size=20)
df = client.sw_industry_page_list(page=1, page_size=20)
df = client.sw_industry_company_page_list(page=1, page_size=20, level_type='level1')

# 融资融券数据
df = client.margin_account_page_list(page=1, page_size=20)
df = client.margin_account_list(limit=50)
df = client.margin_analysis_page_list(page=1, page_size=20)
df = client.margin_analysis_list(limit=50)
df = client.margin_detail_page_list_by_date(page=1, page_size=20)
df = client.margin_detail_page_list_by_stock(page=1, page_size=20)
df = client.margin_detail_list_by_stock(stock_code='000001.SZ', limit=50)
```

## 5. ❌ 错误处理

```python
import datacenter_client as dc
from datacenter_client.exceptions import (
    DatacenterAPIError,
    APIError,
    AuthenticationError,
    NotFoundError,
    InvalidRequestError
)

def safe_api_call():
    try:
        client = dc.init(token='your_api_token')
        df = client.hsgt_fund_page_list(page=1, page_size=10)
        return df

    except AuthenticationError:
        print("❌ 认证失败：请检查API token是否正确")
        return None

    except NotFoundError:
        print("❌ API不存在：请检查API名称是否正确")
        return None

    except InvalidRequestError as e:
        print(f"❌ 请求参数错误：{e}")
        return None

    except DatacenterAPIError as e:
        print(f"❌ API错误：{e.message}")
        return None

    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return None

# 使用
result = safe_api_call()
if result is not None:
    print(f"✅ 成功获取 {len(result)} 条数据")
```

## 6. 📊 分页数据解析

### 识别分页数据
```python
import datacenter_client as dc

client = dc.init(token='your_api_token')

# 调用分页接口
result = client.hsgt_fund_page_list(page=1, page_size=20)

# 检查是否为分页数据
if hasattr(result, 'has_pagination') and result.has_pagination:
    print("✅ 这是分页数据")
    print(f"当前页: {result.current_page}")
    print(f"每页大小: {result.page_size}")
    print(f"总记录数: {result.total_count}")
    print(f"总页数: {result.total_pages}")
else:
    print("✅ 这是普通数据")
    print(f"数据行数: {len(result)}")
```

### 遍历所有分页数据
```python
def get_all_paginated_data(client, api_method, **kwargs):
    """获取所有分页数据的通用函数"""
    all_data = []
    page = 1
    page_size = 100  # 每页大小

    while True:
        try:
            # 调用分页接口
            result = api_method(page=page, page_size=page_size, **kwargs)

            if hasattr(result, 'has_pagination') and result.has_pagination:
                # 分页数据处理
                all_data.extend(result.to_dict('records'))
                print(f"✅ 第 {page} 页，累计 {len(all_data)} 条数据")

                # 检查是否还有下一页
                if page >= result.total_pages:
                    break
                page += 1
            else:
                # 非分页数据
                all_data.extend(result.to_dict('records'))
                break

        except Exception as e:
            print(f"❌ 获取第 {page} 页数据失败：{e}")
            break

    return all_data

# 使用示例
client = dc.init(token='your_api_token')
all_hsgt_data = get_all_paginated_data(
    client,
    client.hsgt_fund_page_list
)
print(f"总共获取 {len(all_hsgt_data)} 条数据")
```

## 7. 📄 非分页数据解析

### 处理普通数据
```python
import pandas as pd
import datacenter_client as dc

client = dc.init(token='your_api_token')

# 调用非分页接口
result = client.hsgt_north_fundxx()

# 检查数据类型
if isinstance(result, pd.DataFrame):
    print(f"✅ 获取到DataFrame，共 {len(result)} 行")
    print(f"列名: {list(result.columns)}")
    print("前5行数据:")
    print(result.head())
else:
    print("✅ 获取到其他格式数据")
    print(f"数据类型: {type(result)}")
    print(f"数据内容: {result}")
```

### 指定返回字段
```python
# 只获取需要的字段
result = client.hsgt_fund_page_list(
    page=1,
    page_size=10,
    fields='trade_date,stock_code,stock_name,hold_market_cap'
)

print("返回的字段:", result.columns.tolist())
print("数据示例:")
print(result.head())
```

## 8. 🛠️ 高级用法

### 配置化客户端
```python
import os
from pathlib import Path
import json

class DataCenterConfig:
    def __init__(self):
        self.api_token = os.getenv('DATACENTER_API_TOKEN')
        self.base_url = os.getenv('DATACENTER_BASE_URL', 'https://data.alphaaidig.com')
        self.timeout = int(os.getenv('DATACENTER_TIMEOUT', '30'))

        # 从配置文件读取
        config_file = Path.home() / '.datacenter' / 'config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.api_token = config.get('api_token', self.api_token)
                self.base_url = config.get('base_url', self.base_url)
                self.timeout = config.get('timeout', self.timeout)

    def get_client(self):
        if not self.api_token:
            raise ValueError("❌ API Token未设置，请设置DATACENTER_API_TOKEN环境变量或配置文件")

        return dc.init(
            token=self.api_token,
            base_url=self.base_url,
            timeout=self.timeout
        )

# 使用
config = DataCenterConfig()
client = config.get_client()
```

### 批量查询
```python
import pandas as pd
from typing import List
import time

def batch_query_stocks(stock_codes: List[str]) -> pd.DataFrame:
    """批量查询多只股票数据"""
    client = dc.init(token='your_api_token')
    all_data = []

    for i, stock_code in enumerate(stock_codes):
        try:
            print(f"📊 查询股票 {stock_code} ({i+1}/{len(stock_codes)})")

            # 这里可以根据需要调用不同的接口
            result = client.a_stock_list(limit=1)  # 示例调用

            # 添加股票代码到结果中（如果接口没有返回）
            if hasattr(result, 'to_dict'):
                data_dict = result.to_dict()
                if isinstance(data_dict, list):
                    all_data.extend(data_dict)
                else:
                    all_data.append(data_dict)

            # 添加延迟避免频率限制
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ 查询股票 {stock_code} 失败：{e}")
            continue

    if all_data:
        return pd.DataFrame(all_data)
    else:
        return pd.DataFrame()

# 使用示例
stock_codes = ['000001', '000002', '600000', '600036']
df = batch_query_stocks(stock_codes)
print(f"总共获取 {len(df)} 条股票数据")
```

### 动态接口调用
```python
def dynamic_api_call(client, api_name: str, **params):
    """动态调用任意API接口"""
    try:
        # 方法一：通过动态属性调用
        api_method = getattr(client, api_name)
        result = api_method(**params)

        # 方法二：通过query方法调用
        # result = client.query(api_name, **params)

        return result

    except AttributeError:
        print(f"❌ 接口 {api_name} 不存在")
        return None
    except Exception as e:
        print(f"❌ 调用接口 {api_name} 失败：{e}")
        return None

# 使用示例
client = dc.init(token='your_api_token')
result = dynamic_api_call(client, 'hsgt_fund_page_list', page=1, page_size=10)
if result is not None:
    print(f"成功获取 {len(result)} 条数据")
```

## 9. ❓ 常见问题

### Q1: 如何获取API Token？
**A**: 请联系系统管理员或访问数据管理后台申请API访问权限。

### Q2: 支持哪些股票代码格式？
**A**:
- A股：基础格式6位数字或带后缀格式，如 "000001", "600000"，"000001.SZ", "600000.SH"
- 港股：基础格式5位数字，如 "00700", "00941", "00700.HK"
- 指数：通常包含后缀，如 "000300.SH", "000905.SZ"

### Q3: 如何知道某个接口是否存在？
**A**:
```python
# 搜索接口
import requests
response = requests.get('http://data.alphaaidig.com/api/v1/docs/search?q=接口名')
if response.status_code == 200:
    results = response.json()
    print(f"找到 {results['total_count']} 个相关接口")
```

### Q4: 如何处理大量数据？
**A**:
1. 每次请求适量数据
2. 正确处理分页信息，避免遗漏数据
3. 添加适当的延迟避免频率限制
4. 使用批量处理提高效率

### Q5: API调用失败怎么办？
**A**:
1. 检查网络连接和base_url是否正确
2. 验证API token是否有效
3. 确认接口名称和参数是否正确
4. 查看错误信息进行针对性处理
5. 使用错误处理机制捕获异常

### Q6: 返回的数据格式是什么？
**A**:
- **分页数据**: PageDataFrame，包含分页信息和数据
- **普通数据**: pandas DataFrame
- **单条记录**: pandas DataFrame（单行）
- **其他**: 根据具体接口可能返回不同格式

### Q7: 如何获取完整的接口文档？
**A**:
```python
import requests

# 获取完整文档
response = requests.get('http://data.alphaaidig.com/api/v1/docs/json')
if response.status_code == 200:
    docs = response.json()
    print(f"总共有 {docs['total_count']} 个接口")
    for api in docs['apis']:
        print(f"- {api['name']}: {api['description']}")
```

### Q8: IDE无法识别动态方法怎么办？
**A**: 现代IDE（如PyCharm、VSCode）会通过运行时学习动态方法，使用几次后就能识别。也可以：
1. 使用 `client.query('方法名')` 的方式调用
2. 添加类型提示注释
3. 确保导入正确的异常类

## 📞 技术支持

如果遇到问题，可以：
1. 查看API错误信息进行调试
2. 访问 http://data.alphaaidig.com/api/v1/docs 查看完整API文档
3. 联系技术支持团队