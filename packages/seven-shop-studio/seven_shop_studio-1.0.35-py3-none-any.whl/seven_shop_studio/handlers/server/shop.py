# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-06 14:37:56
:LastEditTime: 2024-06-18 17:03:25
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.shop.shop_model import *
from seven_shop_studio.models.db_models.shop.shop_postage_model import *

class ShopInfoHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 获取店铺信息
        :last_editors: KangWenBin
        """        
        shop_id = self.request_params["shop_id"]

        shop_model = ShopModel(context=self).get_dict_by_id(shop_id)
        if not shop_model:
            return self.response_json_error("无法获取店铺信息")
        
        postage_list = []
        if shop_model["postage_type"] == 1:
            postage_list = ShopPostageModel(context=self).get_dict_list(where="shop_id = %s", params=[shop_id],field="province_name,postage")
        shop_model["postage_list"] = postage_list
        
        self.response_json_success(shop_model)


    @filter_check_params(["shop_info","shop_id"])
    def post_async(self):
        """
        :description: 店铺信息保存
        :last_editors: KangWenBin
        """
        shop_id = self.request_params["shop_id"]
        shop_info = self.request_params["shop_info"]
        postage_list = self.request_params.get("postage_list",[])

        if shop_info["postage_type"] == 1 and not postage_list:
            return self.response_json_error("邮费配置未填写完整")
        # 参数验证
        check_list = ["wait_pay_time","logistics_time","auto_receipt_time",
                      "consignee","phone","address_info","refund_time","refund_audit","postage_type","postage","shipping_method","remark","coupon_remark"]
        if not self.param_check(shop_info, check_list):
            return self.response_json_error("商品表单未填写完整")

        shop_entity = self.dict_to_entity(Shop(), shop_info) 
        if shop_id > 0:
            # 修改
            shop_entity.id = shop_id
            shop_entity.status = 1
            ShopModel(context=self).update_entity(shop_entity)    
            # 删除旧邮费配置    
            ShopPostageModel(context=self).del_entity(where="shop_id = %s",params=[shop_id])
            if shop_info["postage_type"] == 1:
                # 新增邮费配置
                for item in postage_list:
                    postage_entity = ShopPostage()
                    postage_entity.shop_id = shop_id
                    postage_entity.province_name = item["province_name"]
                    postage_entity.postage = item["postage"]
                    ShopPostageModel(context=self).add_entity(postage_entity)
            return self.response_json_success(desc="提交成功")
        else:
            # 新增
            shop_entity.status = 1
            result = ShopModel(context=self).add_entity(shop_entity)
            if result:
                if shop_info["postage_type"] == 1:
                    # 新增邮费配置
                    for item in postage_list:
                        postage_entity = ShopPostage()
                        postage_entity.shop_id = result
                        postage_entity.province_name = item["province_name"]
                        postage_entity.postage = item["postage"]
                        ShopPostageModel(context=self).add_entity(postage_entity)
            return self.response_json_success(desc="提交成功")
        
