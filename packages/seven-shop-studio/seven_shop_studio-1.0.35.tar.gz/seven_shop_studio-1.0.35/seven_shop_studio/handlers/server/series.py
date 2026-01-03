# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-16 13:39:35
:LastEditTime: 2024-06-05 14:37:28
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.shop.shop_category_model import *
from seven_shop_studio.models.db_models.shop.shop_series_model_ex import *
from seven_shop_studio.models.db_models.shop.shop_category_series_model import *
from seven_shop_studio.models.db_models.goods.goods_model import *



class SeriesListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 系列列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_series_name = self.request_params.get("sel_series_name", None)
        sel_category_id = self.request_params.get("sel_category_id", None)
        sel_status = self.request_params.get("sel_status", None)
        shop_id = self.request_params["shop_id"]
        
        condition = "status > -1 and shop_id = %s"
        param_list = [shop_id]

        if sel_status:
            condition += " and status = %s"
            param_list.append(sel_status)

        if sel_series_name:
            condition += " and series_name like %s"
            param_list.append(f"%{sel_series_name}%")

        if sel_category_id:
            category_series_list = ShopCategorySeriesModel(context=self).get_dict_list(where="category_id = %s",params=sel_category_id,field="series_id")
            if category_series_list:
                condition += " and id in %s"
                param_list.append([x["series_id"] for x in category_series_list])
            else:
                condition += " and 1=2"

        
        series_conn = ShopSeriesModelEx()
        goods_conn = GoodsModel()
        series_list,series_count = series_conn.get_dict_page_list(field="id,sort,series_name,series_picture,series_poster,add_time,status", page_index=page_index,page_size=page_size,order_by="sort desc",where=condition,params=param_list)
        if series_list:
            for item in series_list:
                item["category_name"] = ",".join([x["category_name"] for x in series_conn.get_series_category_list(item["id"])])
                item["goods_count"] = goods_conn.get_total(where="series_id = %s",params=item["id"])

        ret_data = {
            "model_list": series_list,
            "count": series_count,
            "category_list": ShopCategoryModel(context=self).get_dict_list(where="status >-1 and shop_id = %s",params=shop_id,field="id,category_name",order_by="sort desc")
        }

        return self.response_json_success(ret_data)
    


class SeriesInfoHandler(SevenBaseHandler):
    @filter_check_params(["series_id","shop_id"])
    def get_async(self):
        """
        :description: 获取系列信息
        :last_editors: KangWenBin
        """        
        series_id = self.request_params["series_id"]
        shop_id = self.request_params["shop_id"]

        series_model = ShopSeriesModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[series_id,shop_id])
        if not series_model:
            return self.response_json_error("获取系列信息失败")
        series_model["all_category_list"] = ShopCategoryModel(context=self).get_dict_list(where="status >-1 and shop_id = %s",params=shop_id,field="id,category_name",order_by="sort desc")
        series_model["category_list"] = ShopSeriesModelEx().get_series_category_list(series_id)
        self.response_json_success(series_model)

    @filter_check_params(["series_id","series_name","series_picture","sort","shop_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 系列保存
        :last_editors: rigger
        """
        # 分类id(新增给0) 
        series_id = self.request_params["series_id"]
        series_name = self.request_params["series_name"]
        series_picture = self.request_params["series_picture"]
        series_poster = self.request_params.get("series_poster","")
        sort = self.request_params["sort"]
        category_list = self.request_params.get("category_list",[])
        shop_id = self.request_params["shop_id"]

        if not category_list:
            return self.response_json_error("请选择分类信息")
        
        # TODO 执行业务
        series_conn = ShopSeriesModel()
        category_series_conn = ShopCategorySeriesModel()

        if series_id == 0:
            # 新增
            series_entity = ShopSeries()
            series_entity.shop_id = shop_id
            series_entity.series_name = series_name
            series_entity.series_picture = series_picture
            series_entity.series_poster = series_poster
            series_entity.sort = sort
            series_entity.status = 0
            series_entity.add_time = TimeHelper.get_now_timestamp()
            ret = series_conn.add_entity(series_entity)
            if ret:
                for item in category_list:
                    # 新增关联
                    category_series_entity = ShopCategorySeries()
                    category_series_entity.category_id = item
                    category_series_entity.series_id = ret
                    category_series_conn.add_entity(category_series_entity)
            
                return self.response_json_success(desc = "提交成功")
            
        else:
            series_model = series_conn.get_entity_by_id(series_id)
            if not series_model:
                return self.response_json_error("无法获取系列信息")
            
            if series_model.status == 1:
                return self.response_json_error("系列已上架，无法修改")
            
            series_model.series_name = series_name
            series_model.series_picture = series_picture
            series_model.series_poster = series_poster
            series_model.sort = sort

            series_conn.update_entity(series_model)
            # 修改分类关联
            category_series_conn.del_entity(where="series_id = %s",params = series_id)
            for item in category_list:
                # 新增关联
                category_series_entity = ShopCategorySeries()
                category_series_entity.category_id = item
                category_series_entity.series_id = series_id
                category_series_conn.add_entity(category_series_entity)
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["series_id","shop_id"])
    def put_async(self, *args, **kwargs):
        """
        :description: 系列上下架
        :last_editors: rigger
        """
        # 分类id 
        series_id = self.request_params["series_id"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = ShopSeriesModel()
        series_model = conn.get_dict(where="id = %s and shop_id = %s",params=[series_id,shop_id],field="status")
        if not series_model or series_model["status"] == -1:
            return self.response_json_error("无法获取系列信息")

        status = 0
        if series_model["status"] == 0:
            status = 1

        if conn.update_table("status = %s","id = %s",[status,series_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["series_id","shop_id"])
    def delete_async(self, *args, **kwargs):
        """
        :description: 系列删除
        :last_editors: rigger
        """
        # 分类id 
        series_id = self.request_params["series_id"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = ShopSeriesModel()
        series_model = conn.get_dict(where="id = %s and shop_id = %s",params=[series_id,shop_id],field="status")
        if not series_model or series_model["status"] == -1:
            return self.response_json_error("无法获取系列信息")
        
        if series_model["status"] == 1:
            return self.response_json_error("系列已上架，无法删除")

        if conn.update_table("status = -1","id = %s",series_id):
            return self.response_json_success(desc = "提交成功")
        
        self.response_json_error("提交失败")

