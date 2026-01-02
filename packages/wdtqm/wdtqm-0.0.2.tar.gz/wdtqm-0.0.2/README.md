# WdtQimen SDK

旺店通奇门SDK - 用于调用旺店通奇门自定义接口的Python SDK

## 简介

WdtQimen SDK 是一个用于调用旺店通奇门自定义接口的Python SDK。它提供了简单易用的API，支持自动生成奇门签名和旺店通签名，简化了与旺店通系统的集成过程。

## 功能特性

- ✅ 自动生成奇门签名（Qimen Signature）
- ✅ 自动生成旺店通签名（Wangdian Signature）
- ✅ 支持多种业务接口调用
- ✅ 内置调试模式，方便排查问题
- ✅ 完整的错误处理机制
- ✅ 支持JSON参数序列化
- ✅ 类型提示支持
- ✅ 简洁的API设计

## 安装

```bash
pip install wdtqimen
```

## 快速开始

### 基本使用

```python
import wdtqm

# 初始化SDK
sdk = wdtqm.WdtQimenSDK(
    app_key="your_app_key",
    app_secret="your_app_secret",
    target_app_key="your_target_app_key",
    wdt_app_key="your_wdt_app_key",
    wdt_app_secret="your_wdt_app_secret",
    wdt3_customer_id="your_customer_id",
    server_url="your_server_url"
)

# 调用API
result = sdk.call_api(
    method="your_method_name",
    business_params={
        "param1": "value1",
        "param2": "value2"
    }
)

print(result)
```

### 调试模式

```python
# 启用调试模式，查看签名生成过程
result = sdk.call_api(
    method="your_method_name",
    business_params={
        "param1": "value1",
        "param2": "value2"
    },
    debug=True
)

print(result)
```

## 配置说明

### 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_key` | str | 是 | 奇门appkey |
| `app_secret` | str | 是 | 奇门appsecret |
| `target_app_key` | str | 是 | 目标appkey（旺店通在奇门授权的应用） |
| `wdt_app_key` | str | 是 | 旺店通appkey |
| `wdt_app_secret` | str | 是 | 旺店通appsecret（格式：secret:salt） |
| `wdt3_customer_id` | str | 是 | 旺店通客户ID |
| `server_url` | str | 是 | 奇门接口地址 |

### wdt_app_secret 格式说明

`wdt_app_secret` 必须遵循 `secret:salt` 格式，例如：
```
your_secret:your_salt
```

SDK会自动将其拆分为：
- `wdt_secret`: `your_secret`
- `wdt_salt`: `your_salt`

## API 文档

### call_api

调用奇门API的核心方法。

**参数：**
- `method` (str): 接口方法名
- `business_params` (Dict[str, Any], 可选): 业务参数字典
- `debug` (bool, 可选): 是否打印调试信息，默认为False

**返回：**
- Dict[str, Any]: API响应结果

**示例：**
```python
result = sdk.call_api(
    method="your_method_name",
    business_params={
        "src_tid": "your_order_id",
        "page_no": 1,
        "page_size": 10
    }
)
```

### pager_call_api

分页调用API的便捷方法。

**参数：**
- `method` (str): 接口方法名
- `business_params` (Dict[str, Any]): 业务参数字典
- `debug` (bool, 可选): 是否打印调试信息，默认为False

**返回：**
- Dict[str, Any]: API响应结果

**示例：**
```python
result = sdk.pager_call_api(
    method="query_trade",
    business_params={
        "page_no": 1,
        "page_size": 50
    }
)
```

## 签名机制

### 奇门签名

SDK自动生成奇门签名，遵循以下规则：
1. 过滤掉 `sign` 字段
2. 按参数名排序
3. 拼接参数值（布尔值转为小写）
4. 在前后加上 `app_secret`
5. 使用MD5加密

### 旺店通签名

SDK自动生成旺店通签名，遵循以下规则：
1. 递归序列化参数对象
2. 排除特定字段（`wdt3_customer_id`、`wdt_sign`、`target_app_key`）
3. 按键排序
4. 处理特殊类型（布尔值、JSON字符串）
5. 在前后加上 `wdt_secret`
6. 使用MD5加密

## 错误处理

SDK内置了完善的错误处理机制：

```python
try:
    result = sdk.call_api(
        method="your_method",
        business_params={"param": "value"}
    )
except Exception as e:
    print(f"调用失败: {str(e)}")
```

常见错误类型：
- 网络请求失败：检查网络连接和服务器地址
- API调用失败：检查参数和权限
- JSON解析失败：检查返回数据格式

## 调试技巧

### 启用调试模式

```python
result = sdk.call_api(
    method="your_method",
    business_params={"param": "value"},
    debug=True
)
```

调试模式会输出：
- 旺店通签名参数
- 旺店通签名值
- 奇门签名参数
- 奇门签名值

### 常见问题排查

1. **签名错误**
   - 检查 `app_secret` 和 `wdt_app_secret` 是否正确
   - 确认 `wdt_app_secret` 格式为 `secret:salt`
   - 使用调试模式查看签名生成过程

2. **网络错误**
   - 检查 `server_url` 是否正确
   - 确认网络连接正常
   - 检查防火墙设置

3. **参数错误**
   - 确认业务参数格式正确
   - 检查必填参数是否完整
   - 查看API文档了解参数要求

## 系统要求

- Python 3.7+
- requests 2.25.0+

## 依赖项

```txt
requests>=2.25.0
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

## 更新日志

### v0.1.0 (2025-12-29)
- 初始版本发布
- 支持奇门签名生成
- 支持旺店通签名生成
- 支持基础API调用
- 支持调试模式

## 相关链接

- [旺店通奇门文档](https://open.wangdian.cn/qjb/open/guide?path=qjb_guide_qm_customize)
- [奇门签名文档](https://open.taobao.com/doc.htm?docId=101617&docType=1)
