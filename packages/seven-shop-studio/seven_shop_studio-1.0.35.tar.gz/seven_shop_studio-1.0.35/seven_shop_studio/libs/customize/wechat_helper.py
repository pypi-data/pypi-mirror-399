
# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-07 11:37:05
:LastEditTime: 2024-06-14 17:02:46
:LastEditors: KangWenBin
:Description: 
"""
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from seven_framework.time import *
from seven_framework.uuid import *
from seven_framework.http import *
import seven_framework.config as config
from datetime import datetime, timezone
import random
import string
import json

class WechatPayHelper(object):
    def __init__(self) -> None:
        """
        :description: 微信支付初始化
        :last_editors: KangWenBin
        """        
        wechat_pay_config = config.get_value("wechat_pay_config",{})
        self.wechat_app_id = wechat_pay_config.get("wechat_app_id","")
        self.mch_id = wechat_pay_config.get("mch_id","")
        self.notify_url = wechat_pay_config.get("notify_url","")
        self.serial_no = wechat_pay_config.get("serial_no","")
        self.v3_key = wechat_pay_config.get("v3","")
        # 私钥
        with open(wechat_pay_config.get("private_key_path","")) as file:
            private_key = file.read()
        rsa_key = RSA.import_key(private_key)
        self.signer = PKCS1_v1_5.new(rsa_key)
        # 公钥
        with open(wechat_pay_config.get("public_key_path","")) as file:
            public_key = file.read()
        public_rsa_key = RSA.importKey(public_key)
        self.public_signer = PKCS1_v1_5.new(public_rsa_key)
        

    def wechat_jsapi_refund(self,order_id, refund_order_id, refund_price, total_price):
        """
        :description: 微信jsapi支付
        :param: order_id 商户订单号
        :param: title 标题
        :param: price 金额
        :last_editors: KangWenBin
        """        
        ret_data = {
            "result":0,
            "desc":"",
            "data":None
        }

        body = {
            "out_trade_no": order_id,
            "out_refund_no": refund_order_id,
            "notify_url": self.notify_url,
            "amount":{
                "refund": refund_price,
                "total": total_price,
                "currency": "CNY"
            }
        }

        headers = {
            "Authorization": self._create_authorization(json.dumps(body),"POST","/v3/refund/domestic/refunds"),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        result = HTTPHelper.post("https://api.mch.weixin.qq.com/v3/refund/domestic/refunds",json = body, headers = headers)
        if result.status_code == 200:
            refund_data = json.loads(result.text)

            pay_data = {
                "refund_id": refund_data["refund_id"],
                "out_refund_no": refund_data["out_refund_no"],
                "status": refund_data["status"],
                "refund_price": refund_data["amount"]["refund"]
            }

            ret_data["result"] = 1
            ret_data["data"] = pay_data
            return ret_data
        else:
            ret_data["desc"] = result.text
            return ret_data
        
    
    def _create_authorization(self,data,method,url):
        """
        :description: 
        :param {*} data 参数内容
        :param {*} method 请求方式(大写)
        :param {*} url 请求路由
        :last_editors: KangWenBin
        """    
        timestamp = str(TimeHelper.get_now_timestamp())
        nonce_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        sign_list = [method, url, timestamp, nonce_str]
        if data is not None:
            sign_list.append(data)
        else:
            sign_list.append('')
        sign_str = '\n'.join(sign_list) + '\n'
        signature = self._signature_v3(sign_str)
        authorization = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{self.serial_no}"'
        return authorization


    def _signature_v3(self, sign_str):
        """
        :description:  生成V3签名值
        :param private_key_path：私钥路径
        :param sign_str：签名字符串
        """
        try:
            digest = SHA256.new(sign_str.encode('utf-8'))
            return base64.b64encode(self.signer.sign(digest)).decode('utf-8')
        except Exception:
            raise "WeixinPaySignIError"
        

    def check_notify_sign(self, timestamp, nonce, body, response_signature):
        """
        :description: 回调验签
        :last_editors: KangWenBin
        """        

        body = body.decode("utf-8")
        sign_str = f"{timestamp}\n{nonce}\n{body}\n"
        digest = SHA256.new(sign_str.encode('UTF-8'))  # 对响应体进行RSA加密
        return self.public_signer.verify(digest, base64.b64decode(response_signature))  # 验签


    def decode_notify_data(self, ciphertext,nonce,associated_data):
        """
        :description: 微信解密
        :last_editors: KangWenBin
        """        
        cipher = AES.new(self.v3_key.encode(), AES.MODE_GCM, nonce=nonce.encode())
        cipher.update(associated_data.encode())
        en_data = base64.b64decode(ciphertext.encode('utf-8'))
        auth_tag = en_data[-16:]
        _en_data = en_data[:-16]
        plaintext = cipher.decrypt_and_verify(_en_data, auth_tag)
        return plaintext.decode()
    
    
    def iso_to_timestamp(self,iso_time):
        """Convert ISO 8601 formatted string to a timestamp."""
        dt = datetime.fromisoformat(iso_time)  # Convert string to datetime object
        utc_dt = dt.astimezone(timezone.utc)  # Adjust the datetime object to UTC
        return int(utc_dt.timestamp())






