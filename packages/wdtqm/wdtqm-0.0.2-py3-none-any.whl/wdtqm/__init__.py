import hashlib
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List, Union


class WdtQimenSDK:
    """
    旺店通奇门SDK
    
    构造函数形式的SDK, 用于调用旺店通奇门自定义接口
    """
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        target_app_key: str,
        wdt_app_key: str,
        wdt_app_secret: str,
        wdt3_customer_id: str, 
        server_url: str
    ):
        """
        初始化SDK
        
        Args:
            app_key: 奇门appkey
            app_secret: 奇门appsecret
            target_app_key: 目标appkey ( 旺店通在奇门授权的应用 )
            wdt_app_key: 旺店通appkey
            wdt_app_secret: 旺店通appsecret ( 格式: secret:salt )
            wdt3_customer_id: 旺店通客户ID
            server_url: 奇门接口地址
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.target_app_key = target_app_key
        self.wdt_app_key = wdt_app_key
        self.wdt_secret = wdt_app_secret.split(":")[0]
        self.wdt_salt = wdt_app_secret.split(":")[1]
        self.wdt3_customer_id = wdt3_customer_id
        self.server_url = server_url
        
        # 奇门排除签名字段列表
        self.qimen_exclude_sign_fields = ["wdt3_customer_id", "wdt_sign", "target_app_key"]
    
    def is_valid_json(self, content: str) -> bool:
        """
        检查字符串是否为有效的JSON
        
        Args:
            content: 要检查的字符串
            
        Returns:
            是否为有效JSON
        """
        if content is None:
            return False
        
        trimmed_content = content.strip()
        if not ((trimmed_content.startswith("{") and trimmed_content.endswith("}")) or 
                (trimmed_content.startswith("[") and trimmed_content.endswith("]"))):
            return False
        
        try:
            json.loads(trimmed_content)
            return True
        except json.JSONDecodeError:
            return False
    
    def serialize_value_for_signature(self, obj: Any, string_builder: List[str]) -> None:
        """
        递归序列化值用于签名计算
        
        Args:
            obj: 要序列化的对象
            string_builder: 字符串构建器列表
        """
        if isinstance(obj, dict):
            sorted_items = sorted(obj.items())
            for key, value in sorted_items:
                if key in self.qimen_exclude_sign_fields or value is None:
                    continue
                
                string_builder.append(key)
                
                if value is None:
                    continue
                elif isinstance(value, bool):
                    string_builder.append(str(value).lower())
                elif isinstance(value, (int, float)):
                    string_builder.append(str(value))
                elif isinstance(value, str):
                    if self.is_valid_json(value):
                        try:
                            json_obj = json.loads(value)
                            self.serialize_value_for_signature(json_obj, string_builder)
                        except:
                            string_builder.append(value)
                    else:
                        string_builder.append(value)
                else:
                    self.serialize_value_for_signature(value, string_builder)
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    self.serialize_value_for_signature(item, string_builder)
        
        else:
            string_builder.append(str(obj))
    
    def get_qimen_custom_wdt_sign(self, params: Dict[str, Any], method: str) -> str:
        """
        生成奇门自定义接口旺店通签名
        
        Args:
            params: 请求参数字典
            method: API方法名
            
        Returns:
            签名值
        """
        sign_params = params.copy()
        sign_params["method"] = method
        
        string_builder = []
        self.serialize_value_for_signature(sign_params, string_builder)
        
        to_be_signed = self.wdt_secret + ''.join(string_builder) + self.wdt_secret
        
        signature = hashlib.md5(to_be_signed.encode('utf-8')).hexdigest()
        
        return signature
    
    def generate_qimen_signature(self, params: Dict[str, Any]) -> str:
        """
        生成奇门签名
        
        Args:
            params: 参数字典
            
        Returns:
            签名值
        """
        filtered_params = {k: v for k, v in params.items() if k != 'sign'}
        
        sorted_params = dict(sorted(filtered_params.items()))
        
        query_string = self.app_secret
        for key, value in sorted_params.items():
            if value is not None:
                if isinstance(value, bool):
                    query_string += key + str(value).lower()
                elif isinstance(value, (int, float)):
                    query_string += key + str(value)
                else:
                    query_string += key + str(value)
        
        query_string += self.app_secret
        
        return hashlib.md5(query_string.encode('utf-8')).hexdigest().upper()
    
    def call_api(
        self,
        method: str,
        business_params: Dict[str, Any] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        调用奇门API
        
        Args:
            method: 接口方法名
            business_params: 业务参数
            debug: 是否打印调试信息
            
        Returns:
            API响应结果
        """
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        business_params = business_params or {}
        
        wdt_params = {
            "datetime": datetime_str,
            "wdt_appkey": self.wdt_app_key,
            "wdt_salt": self.wdt_salt
        }
        
        all_params = {**wdt_params, **business_params}
        
        wdt_sign = self.get_qimen_custom_wdt_sign(all_params, method)
        all_params["wdt_sign"] = wdt_sign
        
        if debug:
            print(f"旺店通签名参数: {json.dumps(all_params, indent=2, ensure_ascii=False)}")
            print(f"旺店通签名: {wdt_sign}")
        
        qimen_params = {
            "app_key": self.app_key,
            "method": method,
            "timestamp": datetime_str,
            "v": "2.0",
            "sign_method": "md5",
            "format": "json",
            "target_app_key": self.target_app_key,
            "wdt3_customer_id": self.wdt3_customer_id
        }
        
        all_request_params = {**qimen_params, **all_params}
        
        qimen_sign = self.generate_qimen_signature(all_request_params)
        all_request_params["sign"] = qimen_sign
        
        if debug:
            print(f"奇门签名参数: {json.dumps(qimen_params, indent=2, ensure_ascii=False)}")
            print(f"奇门签名: {qimen_sign}")
        
        try:
            response = requests.post(self.server_url, data=all_request_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "error_response" in result:
                error = result["error_response"]
                raise Exception(f"API调用失败: code={error.get('code')}, msg={error.get('msg')}")
            
            return result
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {str(e)}")
    

    def pager_call_api(
        self,
        method: str,
        business_params: Dict[str, Any],
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        查询订单详情
        
        Args:
            method: 接口方法名
            business_params: 业务参数
            debug: 是否打印调试信息
            
        Returns:
            API响应结果
        """
        
        return self.call_api(method, business_params, debug)