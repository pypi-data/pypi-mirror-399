# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2023-06-06 15:54:30
:LastEditTime: 2025-12-31 14:27:19
:LastEditors: KangWenBin
:Description: 
"""

# -*- coding: utf-8 -*-

from seven_studio.handlers.studio_base import *


class SevenBaseHandler(StudioBaseHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write_error(self, status_code, **kwargs):
        """
        @description: 重写全局异常事件捕捉
        @last_editors: Kangwenbin
        """
        self.logger_error.error(traceback.format_exc())
        return self.response_json_error("server error")
    
    def load_json_or_empty(self,data):
        try:
            return json.loads(data)
        except:
            return []
    
    def param_check(self,param,check_list):
        """
        :description: 检查参数完整
        :last_editors: KangWenBin
        """       
        result = True
        for item in check_list:
            if not param.get(item,None):
                if param.get(item,None) == 0:
                    continue
                return False
        return result
    
    def dict_to_entity(self,entity,dict_info):
        """
        :description: 字段转化实体
        :last_editors: KangWenBin
        """        
        field_list = entity.get_field_list()
        for item in field_list:
            if item in dict_info:
                setattr(entity,item,dict_info[item])
        return entity
    
    def get_user_list(self,act_id,user_code_list):
        """
        :description: 获取用户信息列表
        :last_editors: KangWenBin
        """        
        param = {
            "timestamp": TimeHelper.get_now_timestamp(),
            "act_id": act_id,
            "user_code_list": user_code_list
        }
        sign_key = config.get_value("sign_key")
        
        param["sign"] = SignHelper.params_sign_md5(param, sign_key, False, False, False)

        user_info_url = config.get_value("user_info_url")
        result = requests.post(user_info_url,json=param)       
        if result.status_code == 200:
            result_data = json.loads(result.text)
            if result_data["result"] == 1:
                return result_data["data"]
            else:
                return []
        else:
            return []
        

    def finish_json_error(self, desc = "error"):
        finish_dict = dict()
        finish_dict["result"] = 0
        finish_dict["desc"] = desc
        finish_dict["data"] = None
        self.finish(JsonHelper.json_dumps(finish_dict))
    
    def prepare_ext(self):
        """
        @description: 准备方法(签名验证)
        @last_editors: KangWenBin
        """
        if self.request.uri == "/server/refund/notify":
            return
        
        try:
            # 签名参数
            sign_params = {}

            if "Content-Type" in self.request.headers and self.request.headers[
                        "Content-type"].lower().find(
                            "application/json") >= 0 and self.request.body:
                json_params = {}
                try:
                    json_params = json.loads(self.request.body)
                except:
                    return self.finish_json_error("params error")
                    
                if json_params:
                    for field in json_params:
                        sign_params[field] = json_params[field]
            if self.request.arguments and len(self.request.arguments)>0:
                for field in self.request.arguments:
                    sign_params[field] = self.get_param(field)

            # 客户端效验规则
            if not sign_params or len(sign_params) < 2 or "timestamp" not in sign_params or "sign" not in sign_params:
                self.finish_json_error("sign params error!")
                return

            # 请求时间效验
            sign_timestamp = int(sign_params["timestamp"])
            if TimeHelper.add_seconds_by_timestamp(sign_timestamp, 60) < TimeHelper.get_now_timestamp():
                self.finish_json_error("timeout")
                return

            # 构建签名
            sign_key = config.get_value("shop_sign_key")
            build_sign = SignHelper.params_sign_md5(
                sign_params, sign_key, False, False, False)

            if not build_sign or build_sign != sign_params["sign"]:
                self.logger_info.info(
                    f"http请求验签不匹配,收到sign:{sign_params['sign']},构建sign:{build_sign} 加密明文信息:{SignHelper.get_sign_params_str(sign_params,sign_key,False,False)}")
                return self.finish_json_error("sign error!")
        except:
            self.logger_error.error(traceback.format_exc())
            return self.finish_json_error("server error!")