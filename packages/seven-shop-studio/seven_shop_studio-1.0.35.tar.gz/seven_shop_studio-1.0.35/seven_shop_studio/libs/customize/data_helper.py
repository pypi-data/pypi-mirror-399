# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 16:24:05
:LastEditTime: 2024-07-17 13:48:05
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.order.order_model import *
from seven_shop_studio.models.db_models.cart.cart_model_ex import *
from seven_shop_studio.models.db_models.order.order_refund_model_ex import *

class DataHelper:
    @classmethod
    def get_shop_data(self,shop_id,act_id,begin_time,end_time):
        """
        :description: 支付数据提供
        :last_editors: KangWenBin
        """        
        ret_data = {
            "total_price":0, # 总销售额
            "total_count":0, # 总订单量
            "pay_price":0, # 支付金额
            "pay_user":0, # 支付人数
            "pay_count":0, # 支付订单数
            "pay_goods_count":0, # 支付商品件数
            "average_sale":0, # 客单价
            "cart_pay_rate":"0",
            "cart_user":0, # 加购人数
            "cart_goods_count":0, # 加购商品件数
            "refund_price":0, # 成功退款金额
            "refund_user":0, # 成功退款人数
            "refund_count":0, # 成功退款次数
            "refund_rate":"0", # 成功退款率
            "day_list":[] # 每日数据
        }

        # 订单数据
        order_conn = OrderModel()
        ret_data["total_price"] = round(order_conn.get_dict(where="shop_id = %s and pay_time > 0 and act_id = %s",params=[shop_id,act_id],field="ifnull(sum(real_pay_price),0) as total_price")["total_price"],2)
        ret_data["total_count"] = order_conn.get_total(where="shop_id = %s and act_id = %s and pay_time > 0",params=[shop_id,act_id])
        
        order_list = order_conn.get_dict_list(field="real_pay_price,user_code,buy_count,channel_id,add_time", where="shop_id = %s and act_id = %s and add_time >= %s and add_time < %s and pay_time > 0",params=[shop_id,act_id,begin_time,end_time])
        if order_list:
            ret_data["pay_price"] = round(sum([order["real_pay_price"] for order in order_list]),2) 
            ret_data["pay_user"] = len(set([order["user_code"] for order in order_list]))
            ret_data["pay_count"] = len(order_list)
            ret_data["pay_goods_count"] = sum([order["buy_count"] for order in order_list])
            ret_data["average_sale"] = round(ret_data["pay_price"]/ret_data["pay_user"],2)
            ret_data["cart_pay_rate"] = str(int(round(len([x for x in order_list if x["channel_id"] == 2])/ret_data["pay_count"],2)*100))

        # 购物车数据
        cart_list = CartModelEx(context=self).get_cart_list(shop_id,act_id,begin_time,end_time)
        if cart_list:
            ret_data["cart_goods_count"] = sum([cart["buy_count"] for cart in cart_list])
            ret_data["cart_user"] = len(set([cart["user_code"] for cart in cart_list]))
        
        # 退款数据
        refund_conn = OrderRefundModelEx()
        refund_list = refund_conn.get_dict_list(field="real_refund_price,user_code,finish_time",where="shop_id = %s and act_id = %s and finish_time >= %s and finish_time < %s and status = 5 and refund_status = 2",params=[shop_id,act_id,begin_time,end_time])
        if refund_list:
            ret_data["refund_price"] = round(sum([refund["real_refund_price"] for refund in refund_list]),2) 
            ret_data["refund_user"] = len(set([refund["user_code"] for refund in refund_list]))
            ret_data["refund_count"] = len(refund_list)
            
            ret_data["refund_rate"] = "——" if ret_data["pay_count"] <= 0 else str(int(round(ret_data["refund_count"]/ret_data["pay_count"],2)*100))

        while end_time > begin_time:
            day_model = {
                "timestamp": begin_time,
                "day_pay_price":0, # 支付金额
                "day_pay_user":0, # 支付人数
                "day_pay_count":0, # 支付订单数
                "day_pay_goods_count":0, # 支付商品件数
                "day_average_sale":0, # 客单价
                "day_cart_pay_rate":"0%",
                "day_cart_user":0, # 加购人数
                "day_cart_goods_count":0, # 加购商品件数
                "day_refund_price":0, # 成功退款金额
                "day_refund_user":0, # 成功退款人数
                "day_refund_count":0, # 成功退款次数
                "day_refund_rate":"0%" # 成功退款率
            }
            day_order_list = [x for x in order_list if x["add_time"] >= begin_time and x["add_time"] < begin_time + 86400]
            if day_order_list:
                day_model["day_pay_price"] = round(sum([x["real_pay_price"] for x in day_order_list]),2)
                day_model["day_pay_user"] = len(set([x["user_code"] for x in day_order_list]))
                day_model["day_pay_count"] = len(day_order_list)
                day_model["day_pay_goods_count"] = sum([x["buy_count"] for x in day_order_list])
                day_model["day_average_sale"] = round(day_model["day_pay_price"]/day_model["day_pay_user"],2)
                day_model["day_cart_pay_rate"] = str(int(round(len([x for x in day_order_list if x["channel_id"] == 2])/day_model["day_pay_count"],2)*100))
            
            day_cart_list = [x for x in cart_list if x["add_time"] >= begin_time and x["add_time"] < begin_time + 86400]
            if day_cart_list:
                day_model["day_cart_user"] = len(set([x["user_code"] for x in day_cart_list]))
                day_model["day_cart_goods_count"] = sum([x["buy_count"] for x in day_cart_list])
            
            day_refund_list = [x for x in refund_list if x["finish_time"] >= begin_time and x["finish_time"] < begin_time + 86400]
            if refund_list:
                day_model["day_refund_price"] = round(sum([x["real_refund_price"] for x in day_refund_list]),2) 
                day_model["day_refund_user"] = len(set([x["user_code"] for x in day_refund_list]))
                day_model["day_refund_count"] = len(day_refund_list)
                day_model["day_refund_rate"] = "——" if day_model["day_pay_count"] <= 0 else str(int(round(day_model["day_refund_count"]/day_model["day_pay_count"],2)*100))
                
            ret_data["day_list"].append(day_model)
            begin_time += 86400
        return ret_data
    
    def get_user_total_price(self, user_code, act_id, shop_id):
        """
        :description: 获取用户累计消费金额
        :last_editors: KangWenBin
        """        
        user_price = round(OrderModel(context=self).get_dict(where="shop_id = %s and pay_time > 0 and act_id = %s and user_code = %s",params=[shop_id,act_id,user_code],field="ifnull(sum(real_pay_price),0) as total_price")["total_price"],2)
        return user_price
        