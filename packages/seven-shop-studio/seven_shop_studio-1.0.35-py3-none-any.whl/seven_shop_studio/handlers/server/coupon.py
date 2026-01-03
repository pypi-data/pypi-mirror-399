# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-23 16:15:15
:LastEditTime: 2025-12-31 14:26:32
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.coupon.coupon_model_ex import *
from seven_shop_studio.models.db_models.coupon.coupon_goods_model_ex import *
from seven_shop_studio.models.db_models.coupon.coupon_record_model import *
from seven_shop_studio.models.db_models.coupon.coupon_grant_model_ex import *
from seven_shop_studio.libs.customize.data_helper import *

class CouponListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 优惠券列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_coupon_name = self.request_params.get("sel_coupon_name", None)
        sel_status = self.request_params.get("sel_status", None)
        sel_coupon_type = self.request_params.get("sel_coupon_type", None)
        shop_id = self.request_params["shop_id"]
        
        condition = "status > -1 and shop_id = %s"
        param_list = [shop_id]
        
        if sel_coupon_name:
            condition += " and coupon_name like %s"
            param_list.append(f"%{sel_coupon_name}%")

        if sel_status:
            condition += " and status = %s"
            param_list.append(sel_status)

        if sel_coupon_type:
            condition += " and coupon_type = %s"
            param_list.append(sel_coupon_type)

        coupon_conn = CouponModel()
        
        coupon_list,coupon_count = coupon_conn.get_dict_page_list(field="id,coupon_name,coupon_type,use_price,coupon_price,coupon_discount,coupon_inventory,record_number,begin_time,end_time,status,add_time,is_receive", page_index=page_index,page_size=page_size,order_by="id desc",where=condition,params=param_list)
        if coupon_list:
            record_conn = CouponRecordModel()
            # 获取已使用量
            coupon_ids = [item["id"] for item in coupon_list]
            record_list = record_conn.get_dict_list(field="coupon_id,count(id) as used_count", where="coupon_id in %s and status = 1",params=(coupon_ids,), group_by="coupon_id")
            for item in coupon_list:
                item["used_number"] = 0
                record_model = [x for x in record_list if x["coupon_id"] == item["id"]]
                if record_model:
                    item["used_number"] = record_model[0]["used_count"]
                item["last_number"] = item["coupon_inventory"] - item["record_number"]

        ret_data = {
            "model_list": coupon_list,
            "count": coupon_count
        }

        return self.response_json_success(ret_data)


class CouponInfoHandler(SevenBaseHandler):
    @filter_check_params(["coupon_id","shop_id"])
    def get_async(self):
        """
        :description: 获取优惠券信息
        :last_editors: KangWenBin
        """        
        coupon_id = self.request_params["coupon_id"]
        shop_id = self.request_params["shop_id"]
        
        coupon_model = CouponModel(context=self).get_dict(where="id = %s and shop_id = %s", params=[coupon_id,shop_id],field="id,coupon_name,coupon_type,coupon_price,coupon_discount,use_price,coupon_inventory,begin_time,end_time,goods_limit,using_rule,is_receive")
        if not coupon_model:
            return self.response_json_error("获取优惠券信息失败")
        
        coupon_model["goods_list"] = CouponGoodsModelEx(context=self).get_coupon_goods_list(coupon_id)
        
        return self.response_json_success(coupon_model)


    @filter_check_params(["coupon_info","shop_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 优惠券保存
        :last_editors: rigger
        """
        coupon_info = self.request_params["coupon_info"]
        goods_list = self.request_params.get("goods_list")
        shop_id = self.request_params["shop_id"]

        coupon_conn = CouponModel()
        # 参数验证
        coupon_check_list = ["id","coupon_name","coupon_type","goods_limit",
                      "use_price","coupon_inventory","begin_time","end_time","using_rule"]
        if not self.param_check(coupon_info, coupon_check_list):
            return self.response_json_error("优惠券表单未填写完整")
        
        # 判断优惠券金额
        if coupon_info["use_price"] > 0 and coupon_info["coupon_type"] == 0 and coupon_info["coupon_price"] > coupon_info["use_price"]:
            return self.response_json_error("优惠券金额必须小于使用金额")

        # 验证优惠券限制商品
        if coupon_info["goods_limit"] == 1 and not goods_list:
            return self.response_json_error("请选择限制商品")
        
        # 验证优惠券类型
        if coupon_info["coupon_type"] == 0 and coupon_info["coupon_price"] <= 0:
            return self.response_json_error("优惠券金额必须大于0")
        
        if coupon_info["coupon_type"] == 1 and coupon_info["coupon_discount"] <= 0:
            return self.response_json_error("优惠券折扣必须大于0")

        coupon_entity = self.dict_to_entity(Coupon(), coupon_info)
        
        if coupon_entity.id > 0:
            # 修改
            old_coupon_model = coupon_conn.get_entity_by_id(coupon_entity.id)
            if not old_coupon_model:
                return self.response_json_error("优惠券不存在")
            if old_coupon_model.status == 1:
                return self.response_json_error("优惠券已发布，无法修改")
            
            # 验证优惠券库存只能增加，不能减少
            if old_coupon_model.coupon_inventory > coupon_entity.coupon_inventory:
                return self.response_json_error("优惠券库存只能增加，不能减少")
            
            coupon_entity.add_time = old_coupon_model.add_time
            coupon_entity.status = old_coupon_model.status
            coupon_entity.shop_id = old_coupon_model.shop_id
            coupon_entity.record_number = old_coupon_model.record_number
            coupon_conn.update_entity(coupon_entity)
            # 删除原来关联商品
            coupon_goods_conn = CouponGoodsModel()
            coupon_goods_conn.del_entity(where="coupon_id = %s",params=[coupon_entity.id])
            if coupon_info["goods_limit"] == 1:
                # 添加限制商品
                for goods_id in goods_list:
                    coupon_goods_entity = CouponGoods()
                    coupon_goods_entity.coupon_id = coupon_entity.id
                    coupon_goods_entity.goods_id = goods_id
                    coupon_goods_conn.add_entity(coupon_goods_entity)
            return self.response_json_success(desc="提交成功")
                
        else:
            # 新增
            coupon_entity.add_time = TimeHelper.get_now_timestamp()
            coupon_entity.shop_id = shop_id
            coupon_entity.status = 0
            result = coupon_conn.add_entity(coupon_entity)
            if result > 0:
                if coupon_info["goods_limit"] == 1:
                    # 添加限制商品
                    coupon_goods_conn = CouponGoodsModel()
                    for goods_id in goods_list:
                        coupon_goods_entity = CouponGoods()
                        coupon_goods_entity.coupon_id = result
                        coupon_goods_entity.goods_id = goods_id
                        coupon_goods_conn.add_entity(coupon_goods_entity)
                return self.response_json_success(desc="提交成功")
            
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["coupon_id","shop_id"])
    def put_async(self, *args, **kwargs):
        """
        :description: 优惠券上下架
        :last_editors: rigger
        """
        # 优惠券id
        coupon_id = self.request_params["coupon_id"]
        # 店铺id
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        coupon_conn = CouponModel()
        
        coupon_info = coupon_conn.get_dict(where="id = %s and shop_id = %s",params=[coupon_id,shop_id],field="status")
        if not coupon_info or coupon_info["status"] == -1:
            return self.response_json_error("无法获取优惠券信息")

        status = 0
        if coupon_info["status"] == 0:
            status = 1
        
        if status == 0:
            # 判断优惠券是否在投放计划中
            grant_model = CouponGrantModel(context=self).get_dict(where="coupon_id = %s and status = 1",params=[coupon_id],field="id")
            if grant_model:
                return self.response_json_error("该优惠券所绑定投放计划进行中，无法下架")

        if coupon_conn.update_table("status = %s","id = %s",[status,coupon_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["coupon_id","shop_id"])
    def delete_async(self, *args, **kwargs):
        """
        :description: 优惠券删除
        :last_editors: rigger
        """
        # 优惠券id
        coupon_id = self.request_params["coupon_id"]
        # 店铺id
        shop_id = self.request_params["shop_id"]
        
        # TODO 执行业务
        coupon_conn = CouponModel()
        
        coupon_info = coupon_conn.get_dict(where="id = %s and shop_id = %s",params=[coupon_id,shop_id],field="status")
        if not coupon_info or coupon_info["status"] == -1:
            return self.response_json_error("无法获取优惠券信息")
        
        if coupon_info["status"] == 1:
            return self.response_json_error("该优惠券已发布，无法删除")
        
        # 判断优惠券是否在投放计划中
        grant_model = CouponGrantModel(context=self).get_dict(where="coupon_id = %s and status = 1",params=[coupon_id],field="id")
        if grant_model:
            return self.response_json_error("该优惠券所绑定投放计划进行中，无法删除")
        
        if coupon_conn.update_table("status = -1","id = %s",coupon_id):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")


class CouponGrantListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 优惠券投放列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_grant_name = self.request_params.get("sel_grant_name", None)
        sel_grant_type = self.request_params.get("sel_grant_type", None)
        sel_status = self.request_params.get("sel_status", None)
        shop_id = self.request_params["shop_id"]
        
        condition = "a.status > -1 and b.shop_id = %s"
        param_list = [shop_id]

        if sel_status:
            if sel_status == "0": # 未发布
                condition += " and a.status = 0"
            elif sel_status == "1": # 待开始
                condition += " and a.status = 1 and a.begin_time > %s "
                param_list.append(TimeHelper.get_now_timestamp())
            elif sel_status == "2": # 进行中
                condition += " and a.status = 1 and a.begin_time <= %s and a.end_time >= %s "
                param_list.append(TimeHelper.get_now_timestamp())
                param_list.append(TimeHelper.get_now_timestamp())
            elif sel_status == "3": # 已结束
                condition += " and a.status = 1 and a.end_time < %s "
                param_list.append(TimeHelper.get_now_timestamp())

        if sel_grant_name:
            condition += " and a.grant_name like %s"
            param_list.append(f"%{sel_grant_name}%")

        if sel_grant_type:
            condition += " and JSON_CONTAINS(grant_type, %s,'$') "
            param_list.append(f'[{sel_grant_type}]')

        grant_list, grant_count = CouponGrantModelEx(context=self).get_grant_list(page_index,page_size,condition,param_list)
        if grant_list:
            # 获取已投放数量
            for grant_info in grant_list:
                grant_info["grant_type"] = json.loads(grant_info["grant_type"])
                grant_info["grant_count"] = CouponRecordModel(context=self).get_total(where="grant_id = %s",params= grant_info["id"])
                # 状态变更
                if grant_info["grant_status"] == 1:
                    if grant_info["begin_time"] > TimeHelper.get_now_timestamp():
                        grant_info["grant_status"] = 1
                    elif grant_info["end_time"] < TimeHelper.get_now_timestamp():
                        grant_info["grant_status"] = 3
                    elif grant_info["begin_time"] <= TimeHelper.get_now_timestamp() and grant_info["end_time"] >= TimeHelper.get_now_timestamp():
                        grant_info["grant_status"] = 2

        ret_data = {
            "model_list": grant_list,
            "count": grant_count,
            "coupon_list": CouponModel(context=self).get_dict_list(where="status >-1 and shop_id = %s",params=shop_id,field="id,coupon_name",order_by="id desc")
        }

        return self.response_json_success(ret_data)
    

class CouponGrantInfoHandler(SevenBaseHandler):
    @filter_check_params(["grant_id","shop_id"])
    def get_async(self):
        """
        :description: 获取投放信息
        :last_editors: KangWenBin
        """        
        grant_id = self.request_params["grant_id"]
        shop_id = self.request_params["shop_id"]

        grant_model = CouponGrantModel(context=self).get_dict_by_id(grant_id,field="id,grant_name,grant_type,coupon_id,begin_time,end_time,grant_picture")
        if not grant_model:
            return self.response_json_error("获取投放信息失败")
        
        coupon_model = CouponModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[grant_model["coupon_id"],shop_id] ,field="status")
        if not coupon_model:
            return self.response_json_error("获取投放信息归属失败")
        
        grant_model["grant_type"] = json.loads(grant_model["grant_type"])
        self.response_json_success(grant_model)


    @filter_check_params(["grant_info","shop_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 投放保存
        :last_editors: rigger
        """
        grant_info = self.request_params["grant_info"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        grant_conn = CouponGrantModel()
        
        # 参数验证
        field_check_list = ["id","grant_name","coupon_id","begin_time",
                      "end_time","grant_type","grant_picture"]
        if not self.param_check(grant_info, field_check_list):
            return self.response_json_error("投放表单未填写完整")
        
        # 验证优惠券信息
        coupon_model = CouponModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[grant_info["coupon_id"],shop_id] ,field="status")
        if not coupon_model:
            return self.response_json_error("优惠券不存在")

        grant_entity = self.dict_to_entity(CouponGrant(), grant_info)
        
        if grant_entity.id > 0:
            # 修改
            old_grant_model = grant_conn.get_entity_by_id(grant_entity.id)
            if not old_grant_model:
                return self.response_json_error("投放计划不存在")
            
            if old_grant_model.status == 1:
                return self.response_json_error("投放计划已发布，无法修改")
            grant_entity.grant_type = json.dumps(grant_entity.grant_type)
            grant_entity.add_time = old_grant_model.add_time
            grant_entity.status = old_grant_model.status
            grant_conn.update_entity(grant_entity)

            return self.response_json_success(desc="提交成功")
                
        else:
            # 新增
            grant_entity.add_time = TimeHelper.get_now_timestamp()
            grant_entity.status = 0
            grant_entity.grant_type = json.dumps(grant_entity.grant_type)
            result = grant_conn.add_entity(grant_entity)
            if result > 0:
                return self.response_json_success(desc="提交成功")
            
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["grant_id","shop_id"])
    def put_async(self, *args, **kwargs):
        """
        :description: 投放上下架
        :last_editors: rigger
        """
        # 分类id 
        grant_id = self.request_params["grant_id"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = CouponGrantModel()
        grant_model = conn.get_dict_by_id(grant_id,field="status,coupon_id")
        if not grant_model or grant_model["status"] == -1:
            return self.response_json_error("无法获取投放信息")
        
        # 获取优惠券信息
        coupon_model = CouponModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[grant_model["coupon_id"],shop_id] ,field="status")
        if not coupon_model or coupon_model["status"] == -1:
            return self.response_json_error("无法获取优惠券信息")
        
        status = 0
        if grant_model["status"] == 0:
            status = 1

        if status == 1 and coupon_model["status"]!=1:
            return self.response_json_error("该计划所绑定优惠券下架/删除，无法发布")

        if conn.update_table("status = %s","id = %s",[status,grant_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")
        

    @filter_check_params(["grant_id","shop_id"])
    def delete_async(self, *args, **kwargs):
        """
        :description: 投放删除
        :last_editors: rigger
        """
        # 分类id 
        grant_id = self.request_params["grant_id"]
        shop_id = self.request_params["shop_id"]

        # TODO 执行业务
        conn = CouponGrantModel()
        grant_model = conn.get_dict_by_id(grant_id,field="status,coupon_id")
        if not grant_model or grant_model["status"] == -1:
            return self.response_json_error("无法获取投放信息")
        
        # 获取优惠券信息
        coupon_model = CouponModel(context=self).get_dict(where="id = %s and shop_id = %s",params=[grant_model["coupon_id"],shop_id] ,field="status")
        if not coupon_model:
            return self.response_json_error("投放信息异常")

        if grant_model["status"] == 1:
            return self.response_json_error("投放中无法删除")

        if conn.update_table("status = -1","id = %s",grant_id):
            return self.response_json_success(desc = "提交成功")
        
        self.response_json_error("提交失败")
    

class CouponRecordListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 优惠券记录列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_user_code = self.request_params.get("sel_user_code", None)
        sel_coupon_name = self.request_params.get("sel_coupon_name", None)
        sel_status = self.request_params.get("sel_status", None)
        sel_coupon_type = self.request_params.get("sel_coupon_type", None)
        shop_id = self.request_params["shop_id"]
        act_id = str(self.request_params.get("act_id",""))
        
        condition = "shop_id = %s and act_id = %s"
        param_list = [shop_id,act_id]
        
        if sel_user_code:
            condition += " and user_code = %s"
            param_list.append(sel_user_code)

        if sel_coupon_name:
            condition += " and coupon_info like %s"
            param_list.append(f"%{sel_coupon_name}%")

        if sel_status:
            if sel_status == "0":
                condition += " and status = 0 and end_time > %s"
                param_list.append(TimeHelper.get_now_timestamp())
            elif sel_status == "1":
                condition += " and status = 1"
            elif sel_status == "2":
                condition += " and status = 0 and end_time < %s"
                param_list.append(TimeHelper.get_now_timestamp())

        if sel_coupon_type:
            condition += " and JSON_EXTRACT(coupon_info, '$.coupon_type') = %s"
            param_list.append(int(sel_coupon_type))

        
        record_list,record_count = CouponRecordModel(context=self).get_dict_page_list(field="id,user_code,coupon_info,use_price,add_time,status,use_time,end_time", page_index=page_index,page_size=page_size,order_by="id desc",where=condition,params=param_list)
        if record_list:

            # 获取已使用量
            user_code_ids = list(set([item["user_code"] for item in record_list]))
            user_list = self.get_user_list(act_id,user_code_ids)

            for item in record_list:
                coupon_info = json.loads(item["coupon_info"])
                item["coupon_name"] = coupon_info["coupon_name"]
                item["coupon_type"] = coupon_info["coupon_type"]
                item["coupon_content"] = f""
                if item["use_price"] > 0:
                    item["coupon_content"] = f"满{float(item['use_price'])}元,"
                else:
                    item["coupon_content"] = f"无门槛,"
                if item["coupon_type"] == 0:
                    item["coupon_content"] += f" 减{float(coupon_info['coupon_price'])}元"
                else:
                    item["coupon_content"] += f" {float(coupon_info['coupon_discount'])}折"
                
                # 验证优惠券是否过期
                if item["status"] == 0 and item["end_time"] < TimeHelper.get_now_timestamp():
                    item["status"] = 2
                    
                # 获取用户昵称和电话
                item["nick_name"] = item["telephone"] = ""
                user_info = [x for x in user_list if str(x["user_id"]) == item["user_code"]]
                if user_info:
                    item["nick_name"] = user_info[0]["user_nick"]
                    item["telephone"] = user_info[0]["telephone"]
                
                

        ret_data = {
            "model_list": record_list,
            "count": record_count
        }

        return self.response_json_success(ret_data)
    

class CouponUserListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id","user_code"])
    def get_async(self):
        """
        :description: 用户优惠券发放列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        
        shop_id = self.request_params["shop_id"]
        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        
        record_conn = CouponRecordModel()
        record_list,record_count = record_conn.get_dict_page_list(field="id,coupon_info,add_time", page_index=page_index,page_size=page_size,order_by="id desc",where="coupon_source = 2 and user_code = %s and act_id = %s and shop_id = %s",params=[user_code,act_id,shop_id])
        if record_list:
            for item in record_list:
                coupon_info = json.loads(item["coupon_info"])
                item["coupon_name"] = coupon_info["coupon_name"]
                item["coupon_type"] = coupon_info["coupon_type"]
        # 获取当前用户优惠券数量
        user_coupon_count = record_conn.get_total(where="user_code = %s and act_id = %s and shop_id = %s and status = 0 and end_time > %s",params=[user_code,act_id,shop_id,TimeHelper.get_now_timestamp()])
        # 获取可发放优惠券列表
        coupon_list = CouponModel(context=self).get_dict_list(where="shop_id = %s and status = 1 and end_time > %s and coupon_inventory > record_number",params=[shop_id,TimeHelper.get_now_timestamp()],field="id,coupon_name,coupon_type,use_price,coupon_price,coupon_discount")
        ret_data = {
            "model_list": record_list,
            "count": record_count,
            "user_coupon_count": user_coupon_count,
            "coupon_list": coupon_list
        }
        self.response_json_success(ret_data)
    

    @filter_check_params(["shop_id","user_code","coupon_id"])
    def post_async(self):
        """
        :description: 用户优惠券发放
        :last_editors: KangWenBin
        """        
        shop_id = self.request_params["shop_id"]
        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        coupon_id = self.request_params["coupon_id"]

        coupon_conn = CouponModelEx()
        coupon_model = coupon_conn.get_dict(where="id = %s and status = 1 and end_time > %s and coupon_inventory > record_number and shop_id = %s",params=[coupon_id,TimeHelper.get_now_timestamp(),shop_id])
        if not coupon_model:
            return self.response_json_error("优惠券不存在或已失效")
        
        # 获取优惠卷限制商品
        goods_list = CouponGoodsModel(context=self).get_dict_list(where="coupon_id = %s", params=coupon_id)
        
        add_result = 0

        # 优惠券发放
        try:
            if coupon_conn.update_coupon_inventory(coupon_model["id"]):
                record_entity = CouponRecord()
                record_entity.shop_id = shop_id
                record_entity.grant_id = 0
                record_entity.coupon_id = coupon_model["id"]
                record_entity.use_price = coupon_model["use_price"]
                record_entity.goods_limit = coupon_model["goods_limit"]
                record_entity.begin_time = coupon_model["begin_time"]
                record_entity.end_time = coupon_model["end_time"]
                record_entity.user_code = user_code
                record_entity.act_id = act_id
                record_entity.coupon_info = JsonHelper.json_dumps({
                    "coupon_name": coupon_model["coupon_name"],
                    "coupon_type": coupon_model["coupon_type"],
                    "coupon_price": str(coupon_model["coupon_price"]),
                    "coupon_discount": str(coupon_model["coupon_discount"]),
                    "using_rule": coupon_model["using_rule"],
                })
                record_entity.goods_list = json.dumps([x["goods_id"] for x in goods_list if x["coupon_id"] == coupon_model["id"]])
                record_entity.add_time = TimeHelper.get_now_timestamp()
                record_entity.coupon_source = 2
                add_result = CouponRecordModel(context=self).add_entity(record_entity)

        except:
            self.logger_error.error(f"发放优惠券失败,优惠券信息：{coupon_model}，错误信息：{traceback.format_exc()}")
        finally:
            # 优惠券库存效验
            coupon_conn.check_coupon_inventory(coupon_model["id"])

        if add_result:
            return self.response_json_success(desc="发放成功")

        self.response_json_error("发放失败")