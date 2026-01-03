# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2023-09-20 15:25:22
:LastEditTime: 2024-07-17 11:48:36
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.goods.goods_model_ex import *
from seven_shop_studio.models.db_models.goods.goods_sku_model_ex import *
from seven_shop_studio.models.db_models.shop.shop_series_model_ex import *
from seven_shop_studio.models.db_models.inventory.inventory_model_ex import *
from seven_shop_studio.models.db_models.inventory.inventory_change_model import *
from seven_shop_studio.models.db_models.goods.goods_recommend_model_ex import *

from decimal import Decimal


class GoodsListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 商品管理页
        :last_editors: Kangwenbin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_series_id = self.request_params.get("sel_series_id", None)
        sel_goods_name = self.request_params.get("sel_goods_name", None)
        sel_begin_time = self.request_params.get("sel_begin_time", None)
        sel_end_time = self.request_params.get("sel_end_time", None)
        sel_status = self.request_params.get("sel_status", None)
        order_field = self.request_params.get("order_field", None)
        order_by = self.request_params.get("order_by", "desc")
        shop_id = self.request_params["shop_id"]
        
        condition = "a.status > -1 and a.shop_id = %s"
        param_list = [shop_id]

        if sel_status:
            condition += " and a.status = %s"
            param_list.append(sel_status)

        if sel_goods_name:
            condition += " and a.goods_short_name like %s"
            param_list.append(f"%{sel_goods_name}%")

        if sel_series_id:
            condition += " and a.series_id = %s"
            param_list.append(sel_series_id)

        if sel_begin_time:
            condition += " and a.add_time >= %s"
            param_list.append(sel_begin_time)

        if sel_end_time:
            condition += " and a.add_time <= %s"
            param_list.append(sel_end_time)

        if not order_field:
            order_field = "a.sort"
        else:
            order_field = f"a.{order_field}"

        goods_list,goods_count = GoodsModelEx(context=self).get_goods_list(page_index,page_size,condition,f"{order_field} {order_by}",param_list)
        if goods_list:  
            sku_conn = GoodsSkuModelEx()      
            for item in goods_list:
                # 商品主图
                try:
                    item["goods_picture"] = json.loads(item["goods_picture"])[0]
                except:
                    item["goods_picture"] = ""
                item["inventory"] = int(item["inventory"])
                # 获取sku信息
                item["sku_list"] = sku_conn.get_goods_sku_list(item["id"])


        ret_data = {
            "model_list": goods_list,
            "count": goods_count,
            "series_list": ShopSeriesModelEx(context=self).get_dict_list(where="status = 1 and shop_id = %s",params=shop_id,field="id,series_name",order_by="sort desc")
        }

        return self.response_json_success(ret_data)
    

class GoodsInfoHandler(SevenBaseHandler):
    @filter_check_params(["goods_id","shop_id"])
    def get_async(self):
        """
        :description: 获取商品详情
        :last_editors: KangWenBin
        """        
        goods_id = self.request_params["goods_id"]
        shop_id = self.request_params["shop_id"]

        goods_model = GoodsModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[goods_id,shop_id],field="id,series_id,goods_main_images,goods_detail_images,goods_tag_image,goods_long_name,goods_short_name,goods_remark,goods_parameter,goods_service,original_price,price,goods_code,sort,status")
        if not goods_model or goods_model["status"] == -1:
            return self.response_json_error("获取商品信息失败")
        
        # json数据处理
        fields_to_process = ["goods_main_images", "goods_detail_images", "goods_parameter", "goods_service"]
        for field in fields_to_process:
            goods_model[field] = self.load_json_or_empty(goods_model.get(field, '[]'))
        
        # 获取sku信息
        goods_model["sku_info"] = GoodsSkuModelEx(context=self).get_goods_sku_info(goods_id)
        if not goods_model["sku_info"]["sku_list"]:
            # 获取主商品库存
            goods_model["inventory"] = InventoryModelEx(context=self).get_inventory(goods_id,0)
        else:
            goods_model["inventory"] = 0
        
        ret_data = {
            "goods_model": goods_model,
            "series_list": ShopSeriesModelEx(context=self).get_dict_list(where="status = 1 and shop_id = %s",params=shop_id,field="id,series_name",order_by="sort desc")
        }
        self.response_json_success(ret_data)
    
    
    @filter_check_params(["goods_info","shop_id"])
    def post_async(self):
        """
        :description: 商品修改保存
        :last_editors: KangWenBin
        """        
        goods_info = self.request_params["goods_info"]
        shop_id = self.request_params["shop_id"]
        sku_list = self.request_params.get("sku_list",None)
        act_id = str(self.request_params.get("act_id",""))

        goods_conn = GoodsModel()
        sku_conn = GoodsSkuModel()
        
        # 参数验证
        goods_check_list = ["series_id","goods_main_images","goods_detail_images","goods_long_name",
                      "goods_short_name","goods_remark","goods_parameter","goods_service","sort"]
        if not self.param_check(goods_info, goods_check_list):
            return self.response_json_error("商品表单未填写完整")
        
        # 商品赋值
        goods_entity = self.dict_to_entity(Goods(), goods_info) 

        # sku
        sku_entity_list = []
        if sku_list:
            sku_check_list = ["sku_name","sku_info","price","goods_code","inventory","sku_picture"]
            for item in sku_list:
                if not self.param_check(item, sku_check_list):
                    return self.response_json_error("sku表单未填写完整")
                sku_entity = self.dict_to_entity(GoodsSku(),item)
                setattr(sku_entity,"inventory",item["inventory"])
                sku_entity_list.append(sku_entity)
        
        if goods_entity.id > 0:
            # 修改
            old_goods_model = goods_conn.get_entity_by_id(goods_entity.id)
            # old_sku_list = sku_conn.get_list(where="goods_id = %s",params=goods_entity.id)
            if old_goods_model.status == 1:
                return self.response_json_error("商品已上架，无法修改")
            
            goods_entity.goods_sold = old_goods_model.goods_sold
            goods_entity.add_time = old_goods_model.add_time
            goods_entity.shop_id = old_goods_model.shop_id

            # 验证是否有sku
            if sku_entity_list:
                min_sku_entity = min(sku_entity_list, key=lambda x: x.price)
                goods_entity.original_price = min_sku_entity.original_price
                goods_entity.price = min_sku_entity.price
                goods_entity.goods_code = ""
            
            if Decimal(goods_entity.price) <= 0:
                return self.response_json_error("价格错误")
            
            goods_entity.goods_main_images = JsonHelper.json_dumps(goods_entity.goods_main_images)
            goods_entity.goods_detail_images = JsonHelper.json_dumps(goods_entity.goods_detail_images)
            goods_entity.goods_parameter = JsonHelper.json_dumps(goods_entity.goods_parameter)
            goods_entity.goods_service = JsonHelper.json_dumps(goods_entity.goods_service)
            goods_conn.update_entity(goods_entity)

            if not sku_entity_list:
                # 修改商品库存
                inventory_result = self.edit_inventory(goods_entity.id,0,goods_info["inventory"],self.request_user_id(),act_id,"系统库存修改")
                if inventory_result:
                    return self.response_json_success(desc="提交成功")
                else:
                    return self.response_json_error("提交失败")
            
            # 判断sku_id是否都为0
            new_sku_entity = [x for x in sku_entity_list if x.id == 0]
            if new_sku_entity:
                # 新增
                sku_conn.update_table("status = -1","goods_id = %s",goods_entity.id)
                add_result = True
                for item in sku_entity_list:
                    item.goods_id = goods_entity.id
                    item.add_time = TimeHelper.get_now_timestamp()
                    item.sku_info = JsonHelper.json_dumps(item.sku_info)
                    item.status = 1
                    sku_result = sku_conn.add_entity(item)
                    if sku_result:
                        sku_inventory_result = self.edit_inventory(goods_entity.id,sku_result,item.inventory,self.request_user_id(),act_id)
                        add_result = sku_inventory_result if add_result==True else add_result
                if add_result:
                    return self.response_json_success(desc="提交成功")
            else:
                # 循环修改
                for item in sku_entity_list:
                    old_sku_model = sku_conn.get_entity_by_id(item.id)
                    if old_sku_model:
                        item.add_time = old_sku_model.add_time
                        item.goods_id = old_sku_model.goods_id
                        item.sku_info = JsonHelper.json_dumps(item.sku_info)
                        item.status = 1
                        sku_conn.update_entity(item)
                        # 修改库存
                        sku_inventory_result = self.edit_inventory(goods_entity.id,item.id,item.inventory,self.request_user_id(),act_id)
                return self.response_json_success(desc="提交成功")
            
        else:
            # 新增(需验证sku信息是否存在)
            goods_entity.add_time = TimeHelper.get_now_timestamp()
            goods_entity.shop_id = shop_id
            if sku_entity_list:
                # 获取最小的价格sku
                min_sku_entity = min(sku_entity_list, key=lambda x: x.price)
                goods_entity.original_price = min_sku_entity.original_price
                goods_entity.price = min_sku_entity.price
                goods_entity.goods_code = ""
            if Decimal(goods_entity.price) <= 0:
                return self.response_json_error("价格错误")
            
            goods_entity.goods_main_images = JsonHelper.json_dumps(goods_entity.goods_main_images)
            goods_entity.goods_detail_images = JsonHelper.json_dumps(goods_entity.goods_detail_images)
            goods_entity.goods_parameter = JsonHelper.json_dumps(goods_entity.goods_parameter)
            goods_entity.goods_service = JsonHelper.json_dumps(goods_entity.goods_service)
            
            goods_result = goods_conn.add_entity(goods_entity)
            if goods_result:

                # 添加sku信息
                if sku_entity_list:
                    add_result = True
                    for item in sku_entity_list:
                        item.goods_id = goods_result
                        item.add_time = TimeHelper.get_now_timestamp()
                        item.sku_info = JsonHelper.json_dumps(item.sku_info)
                        item.status = 1
                        sku_result = sku_conn.add_entity(item)
                        if sku_result:
                            sku_inventory_result = self.edit_inventory(goods_result,sku_result,item.inventory,self.request_user_id(),act_id)
                            add_result = sku_inventory_result if add_result==True else add_result
                    if add_result:
                        return self.response_json_success(desc="提交成功")
                        
                else:
                    # 添加商品库存信息
                    if self.edit_inventory(goods_result,0,goods_info["inventory"],self.request_user_id(),act_id):
                        return self.response_json_success(desc="提交成功")

                        
                
        self.response_json_error("提交失败")

    def edit_inventory(self,goods_id,sku_id,inventory_number,user_code,act_id,remark = "初始化添加"):
        """
        :description: 修改商品库存
        :last_editors: KangWenBin
        """
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_shopping_center"))
        tran_inventory_conn = InventoryModel(db_transaction=db_transaction)
        tran_inventory_change_conn = InventoryChangeModel(db_transaction=db_transaction)
        
        # 获取旧库存信息
        old_inventory = tran_inventory_conn.get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        if old_inventory:
            # 修改库存信息
            inventory_number = int(inventory_number) - old_inventory["inventory"]
            
            if inventory_number == 0:
                return True
            
            tran_inventory_conn.update_table("inventory = inventory + %s","goods_id = %s and sku_id = %s",[inventory_number,goods_id,sku_id])

            if old_inventory["inventory"] == 0 and inventory_number > 0:
                # 到货通知
                try:
                    self.arrival_notice(goods_id,sku_id)
                except:
                    self.logger_error.error(f"到货通知发送失败：{traceback.format_exc()}")
        else:
            # 添加商品库存信息
            db_transaction.begin_transaction()
            # 库存
            inventory = Inventory()
            inventory.goods_id = goods_id
            inventory.sku_id = sku_id
            inventory.inventory = inventory_number
            tran_inventory_conn.add_entity(inventory)

        # 库存变更记录
        inventory_change = InventoryChange()
        inventory_change.goods_id = goods_id
        inventory_change.sku_id = sku_id
        inventory_change.change_inventory = inventory_number
        inventory_change.add_time = TimeHelper.get_now_timestamp()
        inventory_change.add_user = user_code
        inventory_change.act_id = act_id
        inventory_change.remark = remark
        tran_inventory_change_conn.add_entity(inventory_change)
        if db_transaction.commit_transaction():
            # 库存数量验证
            InventoryModelEx(context=self).check_goods_inventory(goods_id,sku_id)
            return True
        
        return False

    def arrival_notice(self,goods_id,sku_id):
        """
        :description: 到货通知
        :last_editors: rigger
        """
        pass

    @filter_check_params(["goods_list","status","shop_id"])
    def put_async(self, *args, **kwargs):
        """
        :description: 商品上下架
        :last_editors: rigger
        """
        goods_list = self.request_params["goods_list"]
        status = self.request_params["status"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        if GoodsModel(context=self).update_table("status = %s","id in %s and shop_id = %s",[status,goods_list,shop_id]):
            return self.response_json_success("提交成功")
        
        self.response_json_error("提交失败")


    @filter_check_params(["goods_list","shop_id"])
    def delete_async(self, *args, **kwargs):
        """
        :description: 商品删除
        :last_editors: rigger
        """
        # 分类id 
        goods_list = self.request_params["goods_list"]
        shop_id = self.request_params["shop_id"]

        good_model_list = GoodsModel(context=self).get_dict_list(where="id in %s and shop_id = %s",params=[goods_list,shop_id],field="status")
        if good_model_list:
            status = sum([x["status"] for x in good_model_list])
            if status > 0:
                return self.response_json_error("请确认商品已下架后再删除")
        
        # TODO 执行业务
        if GoodsModel(context=self).update_table("status = -1","id in %s and shop_id = %s",[goods_list,shop_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")


class GoodsRecommendListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 推荐商品列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_series_id = self.request_params.get("sel_series_id", None)
        sel_goods_name = self.request_params.get("sel_category_name", None)
        sel_begin_time = self.request_params.get("sel_begin_time", None)
        sel_end_time = self.request_params.get("sel_end_time", None)
        sel_status = self.request_params.get("sel_status", None)
        order_field = self.request_params.get("order_field", None)
        order_by = self.request_params.get("order_by", "desc")
        shop_id = self.request_params["shop_id"]
        
        condition = "b.status > -1 and b.shop_id = %s"
        param_list = [shop_id]

        if sel_status:
            condition += " and b.status = %s"
            param_list.append(sel_status)

        if sel_goods_name:
            condition += " and b.goods_short_name like %s"
            param_list.append(f"%{sel_goods_name}%")

        if sel_series_id:
            condition += " and b.series_id = %s"
            param_list.append(sel_series_id)

        if sel_begin_time:
            condition += " and a.add_time >= %s"
            param_list.append(sel_series_id)

        if sel_end_time:
            condition += " and a.add_time <= %s"
            param_list.append(sel_end_time)

        if not order_field:
            order_field = "a.sort"
        else:
            order_field = f"a.{order_field}"

        goods_list,goods_count = GoodsModelEx(context=self).get_goods_recommend_list(page_index,page_size,condition,f"{order_field} {order_by}",param_list)
        if goods_list:  
            sku_conn = GoodsSkuModelEx()      
            for item in goods_list:
                # 商品主图
                try:
                    item["goods_picture"] = json.loads(item["goods_picture"])[0]
                except:
                    item["goods_picture"] = ""
                # 获取sku信息
                item["sku_list"] = sku_conn.get_goods_sku_list(item["goods_id"])


        ret_data = {
            "model_list": goods_list,
            "count": goods_count,
            "series_list": ShopSeriesModelEx(context=self).get_dict_list(where="status = 1 and shop_id = %s",params=shop_id,field="id,series_name")
        }

        return self.response_json_success(ret_data)
    
    @filter_check_params(["shop_id","goods_id_list"])
    def post_async(self):
        """
        :description: 导入商品
        :last_editors: KangWenBin
        """
        shop_id = self.request_params["shop_id"]
        goods_id_list = self.request_params["goods_id_list"]
        
        success_list = []
        fail_list = []

        # 判断商品是否已经存在
        goods_list = GoodsModelEx(context=self).get_dict_list(where="status > -1 and shop_id = %s and id in %s",params=[shop_id,goods_id_list],field="id")
        if goods_list:
            conn = GoodsRecommendModelEx()
            for item in goods_list:
                # 验证是否已经存在推荐列表中
                if not conn.get_dict(where="goods_id = %s",params=[item["id"]]):
                    recommend_entity = GoodsRecommend()
                    recommend_entity.goods_id = item["id"]
                    recommend_entity.sort = conn.get_recommend_sort()
                    recommend_entity.add_time = TimeHelper.get_now_timestamp()
                    result = conn.add_entity(recommend_entity)
                    success_list.append(result)
                else:
                    fail_list.append(item["id"])
            if len(success_list) == 0 and len(fail_list) > 0:
                return self.response_json_error("商品已在推荐列表中")
            else:
                return self.response_json_success(desc="提交成功")
            
        else:
            return self.response_json_error("无法获取商品列表")
        
    @filter_check_params(["goods_id","sort"])
    def put_async(self):
        """
        :description: 修改推荐商品排序
        :last_editors: KangWenBin
        """
        goods_id = self.request_params["goods_id"]
        sort = self.request_params["sort"]

        GoodsRecommendModel(context=self).update_table("sort = %s","goods_id = %s",[sort,goods_id])
        return self.response_json_success(desc="提交成功")
    
    @filter_check_params(["goods_id"])
    def delete_async(self):
        """
        :description: 删除推荐商品
        :last_editors: KangWenBin
        """
        goods_id = self.request_params["goods_id"]

        if GoodsRecommendModel(context=self).del_entity(where="goods_id = %s",params=[goods_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")

        
    