# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-22 14:49:26
:LastEditTime: 2024-07-19 16:16:43
:LastEditors: KangWenBin
:Description: 
"""
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_shop_studio.handlers.seven_base import SevenBaseHandler
from seven_shop_studio.models.db_models.order.order_model_ex import *
from seven_shop_studio.models.db_models.order.order_goods_models_ex import *
from seven_shop_studio.models.db_models.order.order_refund_model_ex import *
from seven_shop_studio.models.db_models.order.order_refund_goods_model import *
from seven_shop_studio.libs.customize.coupon_helper import *
from seven_shop_studio.libs.customize.wechat_helper import *

class OrderListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id","act_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 订单列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_order_id = self.request_params.get("sel_order_id", None)
        sel_goods_name = self.request_params.get("sel_goods_name", None)
        sel_user_code = self.request_params.get("sel_user_code", None)
        sel_status = self.request_params.get("sel_status",None)
        sel_begin_time = self.request_params.get("sel_begin_time", None)
        sel_end_time = self.request_params.get("sel_end_time", None)
        shop_id = self.request_params["shop_id"]
        act_id = self.request_params["act_id"]
        is_excel = int(self.request_params.get("is_excel", "0"))

        condition = "a.shop_id = %s and a.act_id = %s"
        param_list = [shop_id,act_id]

        if sel_order_id:
            condition += " and a.order_id = %s"
            param_list.append(sel_order_id)

        if sel_goods_name:
            condition += " and b.goods_name like %s"
            param_list.append(f"%{sel_goods_name}%")

        if sel_user_code:
            condition += " and a.user_code = %s"
            param_list.append(sel_user_code)

        if sel_status:
            condition += " and a.status = %s"
            param_list.append(sel_status)

        if sel_begin_time:
            condition += " and a.add_time >= %s"
            param_list.append(sel_begin_time)

        if sel_end_time:
            condition += " and a.add_time <= %s"
            param_list.append(sel_end_time)

        if is_excel == 1:
            order_list,order_count = OrderModelEx(context=self).get_order_excel_page_list(page_index,page_size,condition,param_list)
        else:
            order_list,order_count = OrderModelEx(context=self).get_order_page_list(page_index,page_size,condition,param_list)
        if order_list:
            user_code_ids = list(set([item["user_code"] for item in order_list]))
            user_list = self.get_user_list(act_id,user_code_ids)

            if is_excel == 0:
                # 获取订单对应的商品信息
                order_id_list = [x["order_id"] for x in order_list]
                # 订单商品列表
                order_goods_list = OrderGoodsModelEx(context=self).get_order_goods_list(order_id_list)

            for item in order_list:
                if is_excel == 0:
                    item["order_goods_list"] = [x for x in order_goods_list if x["order_id"] == item["order_id"]]
                else:
                    # 商品退款状态 # 0 无退款 1 退款中 2 退款成功 3 退款失败
                    if item["refund_status"] == 0:
                        item["refund_status"] = "商家审核中"
                    elif item["refund_status"] == 1:
                        item["refund_status"] = "通过售后"
                    elif item["refund_status"] == 2:
                        item["refund_status"] = "拒绝售后"
                    elif item["refund_status"] == 3:
                        item["refund_status"] = "商品寄回中"
                    elif item["refund_status"] == 4:
                        item["refund_status"] = "退款撤销"
                    elif item["refund_status"] == 5:
                        item["refund_status"] = "退款成功"
                    elif item["refund_status"] == 6:
                        item["refund_status"] = "退款失败"
                    
                    # 合并省市县
                    item["address_info"] = f"{item['province_name']} {item['city_name']} {item['district_name']} {item['address_info']}"
                    # 时间戳转换
                    item["add_time"] = "" if item["add_time"] == 0 else TimeHelper.timestamp_to_format_time(item["add_time"])
                    item["logistics_time"] = "" if item["logistics_time"] == 0 else TimeHelper.timestamp_to_format_time(item["logistics_time"])
                    # 单价计算
                    item["unit_price"] = round(item["price"] / item["buy_count"],2)
                    
                item["nick_name"] = ""
                user_info = [x for x in user_list if str(x["user_id"]) == item["user_code"]]
                if user_info:
                    item["nick_name"] = user_info[0]["user_nick"]


        ret_data = {
            "model_list": order_list,
            "count": order_count
        }

        return self.response_json_success(ret_data)
    

class OrderInfoHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def get_async(self):
        """
        :description: 订单详情
        :last_editors: KangWenBin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]
        
        order_model = OrderModel(context=self).get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="order_id,add_time,status,province_name,city_name,district_name,consignee,phone,address_info,logistics_company,logistics_number,pay_order_id,pay_time,price,real_pay_price,postage,coupon_price")
        if not order_model:
            return self.response_json_error("无法获取订单信息")

        order_goods_list = OrderGoodsModelEx(context=self).get_order_goods_list([order_id])
        order_model["goods_list"] = order_goods_list
        ret_data = {
            "order_info":order_model
        }
        return self.response_json_success(ret_data)
        

    @filter_check_params(["order_id","logistics_status","shop_id"])
    def post_async(self):
        """
        :description: 订单发货
        :last_editors: KangWenBin
        """        
        order_id = self.request_params["order_id"]
        logistics_status = self.request_params["logistics_status"] # 0 不予发货 1 发货 2 取消不予发货
        logistics_company = self.request_params.get("logistics_company",None)
        logistics_number = self.request_params.get("logistics_number",None)
        logistics_time = self.request_params.get("logistics_time",None)
        shop_id = self.request_params["shop_id"]

        order_conn = OrderModel()
        
        if not logistics_time:
            logistics_time = TimeHelper.get_now_timestamp()

        order_model = order_conn.get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status")
        if not order_model:
            return self.response_json_error("无法获取订单信息")
        
        if logistics_status in [0,1]:
            if order_model["status"] not in [2,3]:
                return self.response_json_error("订单状态异常")
            
            if logistics_status == 0:
                if order_conn.update_table("status = 5,logistics_time = %s","order_id = %s",[logistics_time,order_id]):
                    return self.response_json_success(desc="提交成功")
            elif logistics_status == 1:
                if not logistics_company or not logistics_number:
                    return self.response_json_error("发货信息异常")
                
                if order_conn.update_table("status = 3,logistics_company=%s,logistics_number= %s,logistics_time = %s","order_id = %s",[logistics_company,logistics_number,logistics_time,order_id]):
                    try:
                        self.success_extend(order_id)
                    except:
                        self.logger_error.error(f"扩展方法错误:{traceback.format_exc()}")
                    return self.response_json_success(desc="提交成功")
        
        elif logistics_status == 2:
            if order_model["status"] != 5:
                return self.response_json_error("订单状态异常")
            
            if order_conn.update_table("status = 2,logistics_time = 0","order_id = %s",[order_id]):
                    return self.response_json_success(desc="提交成功")
        
        else:
            return self.response_json_error("参数错误")
        
        self.response_json_error("提交失败")


    def success_extend(self,order_id):
        """
        :description: 发货成功扩展方法
        :last_editors: KangWenBin
        """
        pass


    @filter_check_params(["remark","order_id","shop_id"])
    def put_async(self):
        """
        :description: 设置备注
        :last_editors: KangWenBin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]
        remark = self.request_params["remark"]

        if OrderModel(context=self).update_table("shop_remark = %s","order_id = %s and shop_id = %s",[remark,order_id,shop_id]):
            return self.response_json_success(desc="提交成功")
        
        self.response_json_error("提交失败")


class RefundOrderListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 订单列表
        :last_editors: KangWenBin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        sel_user_code = self.request_params.get("sel_user_code", None)
        sel_order_id = self.request_params.get("sel_order_id", None)
        sel_refund_order_id = self.request_params.get("sel_refund_order_id", None)
        sel_logistics_status = self.request_params.get("sel_logistics_status", None)
        sel_refund_type = self.request_params.get("sel_refund_type", None)
        sel_goods_name = self.request_params.get("sel_goods_name", None)
        sel_status = self.request_params.get("sel_status",None)
        sel_begin_time = self.request_params.get("sel_begin_time", None)
        sel_end_time = self.request_params.get("sel_end_time", None)
        shop_id = self.request_params["shop_id"]
        is_excel = int(self.request_params.get("is_excel", "0"))
        act_id = self.request_params["act_id"]

        condition = "a.shop_id = %s and a.act_id = %s"
        param_list = [shop_id,act_id]

        if sel_order_id:
            condition += " and a.order_id = %s"
            param_list.append(sel_order_id)

        if sel_user_code:
            condition += " and a.user_code = %s"
            param_list.append(sel_user_code)

        if sel_refund_order_id:
            condition += " and a.refund_order_id = %s"
            param_list.append(sel_refund_order_id)

        if sel_logistics_status:
            if sel_logistics_status == "0":
                condition += " and b.logistics_number = ''"
            else:
                condition += " and b.logistics_number != ''"
        
        if sel_refund_type:
            condition += " and a.refund_type = %s"
            param_list.append(sel_refund_type)

        if sel_goods_name:
            condition += " and c.goods_name like %s"
            param_list.append(f"%{sel_goods_name}%")

        if sel_status:
            condition += " and a.status = %s"
            param_list.append(sel_status)

        if sel_begin_time:
            condition += " and a.add_time >= %s"
            param_list.append(sel_begin_time)

        if sel_end_time:
            condition += " and a.add_time <= %s"
            param_list.append(sel_end_time)

        if is_excel == 1:
            refund_order_list,refund_order_count = OrderRefundModelEx(context=self).get_refund_order_excel_page_list(page_index,page_size,condition,param_list)
        else:
            refund_order_list,refund_order_count = OrderRefundModelEx(context=self).get_refund_order_page_list(page_index,page_size,condition,param_list)
        if refund_order_list:
            if is_excel == 0:
                # 获取订单对应的商品信息
                refund_order_id_list = [x["refund_order_id"] for x in refund_order_list]
                # 订单商品列表
                refund_order_goods_list = OrderRefundGoodsModel(context=self).get_dict_list(where="refund_order_id in %s",params=(refund_order_id_list,),field="refund_order_id,sku_name,goods_name,goods_picture,refund_count,refund_price")

            for item in refund_order_list:
                if is_excel == 0:
                    item["refund_order_goods_list"] = [x for x in refund_order_goods_list if x["refund_order_id"] == item["refund_order_id"]]
                else:
                    user_code_ids = list(set([item["user_code"] for item in refund_order_list]))
                    user_list = self.get_user_list(act_id,user_code_ids)

                    item["nick_name"] = ""
                    user_info = [x for x in user_list if str(x["user_id"]) == item["user_code"]]
                    if user_info:
                        item["nick_name"] = user_info[0]["user_nick"]

                    # 合并省市县
                    item["address_info"] = f"{item['province_name']} {item['city_name']} {item['district_name']} {item['address_info']}"
                    # 时间戳转换
                    item["order_time"] = "" if item["order_time"] == 0 else TimeHelper.timestamp_to_format_time(item["order_time"])
                    item["refund_time"] = "" if item["refund_time"] == 0 else TimeHelper.timestamp_to_format_time(item["refund_time"])
                    # 单价计算
                    item["unit_price"] = round(item["price"] / item["buy_count"],2)

        ret_data = {
            "model_list": refund_order_list,
            "count": refund_order_count
        }

        return self.response_json_success(ret_data)
    

class RefundOrderInfoHandler(SevenBaseHandler):

    @filter_check_params(["refund_order_id","refund_status","shop_id"])
    def post_async(self):
        """
        :description: 退款/审核
        :last_editors: KangWenBin
        """        
        refund_order_id = self.request_params["refund_order_id"]
        refund_status = self.request_params["refund_status"] # 1 通过 2 拒绝
        remark = self.request_params.get("remark", "")
        shop_id = self.request_params["shop_id"]

        refund_conn = OrderRefundModelEx()
        refund_model = refund_conn.get_dict(where="refund_order_id = %s and shop_id = %s",params=[refund_order_id,shop_id],field="refund_type,status,order_id,real_refund_price")
        if not refund_model:
            return self.response_json_error("退款单不存在")
        
        refund_mark = 0 # 是否需要退款标识

        if refund_model["status"] == 0: # 审核
            if refund_conn.update_table("status = %s,pass_time = %s,pass_remark = %s","refund_order_id = %s",[refund_status,TimeHelper.get_now_timestamp(),remark,refund_order_id]):
                if refund_model["refund_type"] == 1 and refund_status == 1:
                    refund_mark = 1
                else:
                    return self.response_json_success(desc="提交成功")
                
        elif refund_model["status"] == 3:
            if refund_status == 1:
                refund_mark = 1

            else:
                # 拒绝
                if refund_conn.update_table("status = 6,pass_time = %s,pass_remark = %s","refund_order_id = %s",[TimeHelper.get_now_timestamp(),remark,refund_order_id]):
                    return self.response_json_success(desc="提交成功")
        
        else:
            return self.response_json_error("退款单状态异常")

        if refund_mark == 1:
            # 退款
            order_model = OrderModel(context=self).get_dict(where="order_id = %s",params=refund_model["order_id"],field="real_pay_price,coupon_id")
            if not order_model:
                return self.response_json_error("无法获取订单信息")
            
            # 判断退款金额和优惠券信息
            if refund_model["real_refund_price"]>0:
                # 通过(调用微信退款)
                refund_result = WechatPayHelper().wechat_jsapi_refund(order_id=refund_model["order_id"],refund_order_id=refund_order_id,refund_price=int(refund_model["real_refund_price"]*100),total_price=int(order_model["real_pay_price"]*100))
                if refund_result["result"] == 1:
                    # 退款成功(更新退款单状态)
                    if refund_conn.update_table("refund_status = 1,refund_pay_id = %s","refund_order_id = %s",[refund_result["data"]["refund_id"],refund_order_id]):
                        return self.response_json_success(desc="提交成功")
                    else:
                        return self.response_json_error("提交失败")
                else:
                    # 退款失败
                    self.logger_error.error(f"退款失败,退款单号:{refund_order_id},error_msg:{refund_result['desc']}")
                    refund_conn.update_table("refund_status = 3,refund_info = %s","refund_order_id = %s",[refund_result["desc"],refund_order_id])
                    return self.response_json_error(f"退款失败:{refund_result['desc']}")
            else:
                # 无需退款，直接更改退款单状态
                if refund_conn.update_table("status = 5,finish_time = %s","refund_order_id = %s",[TimeHelper.get_now_timestamp(),refund_order_id]):
                    # 验证是否所有商品都已退款
                    if refund_conn.check_refund_complete(refund_model["order_id"]):
                        # 退还优惠券
                        CouponRecordModel(context=self).update_table("order_id = '',use_time = 0,status = 0","id = %s",order_model["coupon_id"])
                        # 修改订单状态为已取消
                        OrderModel(context=self).update_table("status = 1,finish_time = %s,sync_status = 0","order_id = %s",[TimeHelper.get_now_timestamp(),refund_model["order_id"]])
                    return self.response_json_success(desc="提交成功") 
                    
            
        self.response_json_error("提交失败")

    
class RefundNotifyHandler(SevenBaseHandler):
    def post_async(self):
        """
        @description: 微信退款回调
        @last_editors: KangWenBin
        """
        wechat_helper = WechatPayHelper()
        # 微信支付验签
        headers = self.request.headers._dict
        timestamp = headers.get("Wechatpay-Timestamp", None)
        nonce = headers.get("Wechatpay-Nonce", None)
        signature = headers.get("Wechatpay-Signature", None)

        data = self.request.body
        # self.logger_info.info(f"timestamp:{timestamp},nonce:{nonce},signature:{signature},data:{data}")
        if wechat_helper.check_notify_sign(timestamp,nonce,data,signature):
            # 验签通过
            data = json.loads(data)
            
            # data解密
            pay_string =  wechat_helper.decode_notify_data(data["resource"]["ciphertext"],data["resource"]["nonce"],data["resource"]["original_type"])
            pay_data = json.loads(pay_string)

            refund_order_id = pay_data["out_refund_no"]
            refund_conn = OrderRefundModelEx()
            refund_model = refund_conn.get_dict(where="refund_order_id = %s",params = refund_order_id,field="status,real_refund_price,order_id")
            if not refund_model:
                self.logger_error.error(f"退款回调:无法获取退款单信息,refund_order_id:{refund_order_id}")
                return self.write("success")
            
            order_model = OrderModel(context=self).get_dict(where="order_id = %s",params = refund_model["order_id"],field="coupon_id")
            if not order_model:
                self.logger_error.error(f"退款回调:无法获取订单信息,order_id:{refund_model['order_id']}")
                return self.write("success")
            
            # 验证退款金额
            if int(refund_model["real_refund_price"]*100) != pay_data["amount"]["refund"]:
                self.logger_error.error(
                    f"微信退款订单[{refund_order_id}] 金额不匹配.数据库金额:{refund_model['real_refund_price']*100} 平台回调金额:{pay_data['amount']['refund']};")
                return self.write("error")

            if pay_data["refund_status"] == "SUCCESS": # 退款成功
                # 修改退款单状态
                if refund_conn.update_table(update_sql="status = 5,refund_status = 2,refund_info = %s,finish_time = %s",where="refund_order_id = %s",params = [data["summary"],TimeHelper.get_now_timestamp(),refund_order_id]):
                    # 验证是否所有商品都已退款
                    if refund_conn.check_refund_complete(refund_model["order_id"]):
                        # 退还优惠券
                        CouponRecordModel(context=self).update_table("order_id = '',use_time = 0,status = 0","id = %s",order_model["coupon_id"])
                        # 修改订单状态为已取消
                        OrderModel(context=self).update_table("status = 1,finish_time = %s,sync_status = 0","order_id = %s",[TimeHelper.get_now_timestamp(),refund_model["order_id"]])
                    
                    try:
                        self.success_extend(refund_order_id)
                    except:
                        self.logger_error.error(f"微信退款订单[{refund_order_id}] 扩展方法执行失败,error_msg:{traceback.format_exc()}")
                    return self.write("success")
            else:
                # 退款失败
                if refund_conn.update_table(update_sql="status = 6,refund_status = 3,refund_info = %s,finish_time = %s",where="refund_order_id = %s",params = [f"{pay_data['refund_status']}_{data['summary']}",TimeHelper.get_now_timestamp(),refund_order_id]):
                    return self.write("success")

        else:
            self.logger_error.error(f"微信验签失败,data:{data}")
            return self.write("success")
        

        self.write("success")

    def success_extend(self,refund_order_id):
        """
        :description: 退款成功扩展方法
        :last_editors: KangWenBin
        """        
        pass