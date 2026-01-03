# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-16 13:39:35
:LastEditTime: 2024-06-05 16:12:04
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.shop.shop_category_model import *
from seven_shop_studio.models.db_models.shop.shop_series_model_ex import *



class CategoryListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 分类列表
        :last_editors: KangWenBin
        """        
        
        shop_id = self.request_params["shop_id"]
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_category_name = self.request_params.get("sel_category_name", None)
        sel_status = self.request_params.get("sel_status", None)
        
        condition = "status > -1 and shop_id = %s"
        param_list = [shop_id]

        if sel_status:
            condition += " and status = %s"
            param_list.append(sel_status)

        if sel_category_name:
            condition += " and category_name like %s"
            param_list.append(f"%{sel_category_name}%")

        category_list,category_count = ShopCategoryModel(context=self).get_dict_page_list(field="id,category_name,status,add_time,sort", page_index=page_index,page_size=page_size,order_by="sort desc",where=condition,params=param_list)
        if category_list:
            series_conn = ShopSeriesModelEx()
            for item in category_list:
                item["series_count"] = series_conn.get_category_series_count(item["id"])

        ret_data = {
            "model_list": category_list,
            "count": category_count
        }

        return self.response_json_success(ret_data)
    


class CategoryInfoHandler(SevenBaseHandler):

    @filter_check_params(["id","category_name","sort","shop_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 分类保存
        :last_editors: rigger
        """
        # 分类id(新增给0) 
        id = self.request_params["id"]
        # 分类名称 
        category_name = self.request_params["category_name"]
        # 排序(数字大的排前面) 
        sort = self.request_params["sort"]
        # 店铺id
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = ShopCategoryModel()
        if id == 0:
            # 新增
            category_entity = ShopCategory()
            category_entity.shop_id = shop_id
            category_entity.category_name = category_name
            category_entity.sort = sort
            category_entity.status = 0
            category_entity.add_time = TimeHelper.get_now_timestamp()
            ret = conn.add_entity(category_entity)
            if ret:
                return self.response_json_success(desc = "提交成功")
            
        else:
            category_model = conn.get_entity_by_id(id)
            if not category_model:
                return self.response_json_error("无法获取分类信息")

            if category_model.status == 1:
                return self.response_json_error("分类已发布，无法修改")

            category_model.category_name = category_name
            category_model.sort = sort

            conn.update_entity(category_model)
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["category_id","shop_id"])
    def put_async(self, *args, **kwargs):
        """
        :description: 分类上下架
        :last_editors: rigger
        """
        # 分类id 
        category_id = self.request_params["category_id"]
        # 店铺id
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = ShopCategoryModel()
        category_model = conn.get_dict(where="id = %s and shop_id = %s",params=[category_id,shop_id],field="status")
        if not category_model or category_model["status"] == -1:
            return self.response_json_error("无法获取分类信息")

        status = 0
        if category_model["status"] == 0:
            status = 1

        if conn.update_table("status = %s","id = %s",[status,category_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["category_id","shop_id"])
    def delete_async(self, *args, **kwargs):
        """
        :description: 分类删除
        :last_editors: rigger
        """
        # 分类id 
        category_id = self.request_params["category_id"]
        # 店铺id
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = ShopCategoryModel()
        category_model = conn.get_dict(where="id = %s and shop_id = %s",params=[category_id,shop_id],field="status")
        if not category_model or category_model["status"] == -1:
            return self.response_json_error("无法获取分类信息")
        
        if category_model["status"] == 1:
            return self.response_json_error("分类已发布，无法删除")

        if conn.update_table("status = -1","id = %s",category_id):
            return self.response_json_success(desc = "提交成功")
        
        self.response_json_error("提交失败")

