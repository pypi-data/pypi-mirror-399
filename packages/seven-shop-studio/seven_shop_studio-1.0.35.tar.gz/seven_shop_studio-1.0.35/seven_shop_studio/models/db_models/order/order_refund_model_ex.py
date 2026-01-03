# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-04 10:16:19
:LastEditTime: 2024-07-10 16:40:49
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.order.order_refund_model import *
from seven_shop_studio.models.db_models.order.order_goods_model import *

class OrderRefundModelEx(OrderRefundModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)
    
    def get_refund_order_page_list(self, page_index, page_size, where='', params=None):
        """
        :description: 退款订单列表
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" where {where}"


        sql = f"SELECT a.order_id,a.refund_order_id,a.add_time,IF(b.logistics_number = '',0,1) AS logistics_status,a.real_refund_price,a.refund_type,a.reason,a.status  FROM order_refund_tb a  JOIN order_tb b ON a.order_id = b.order_id JOIN order_refund_goods_tb c ON a.refund_order_id = c.refund_order_id {condition} GROUP BY a.refund_order_id ORDER BY a.add_time desc {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT COUNT(*) as order_count FROM (SELECT a.order_id FROM order_refund_tb a  JOIN order_tb b ON a.order_id = b.order_id JOIN order_refund_goods_tb c ON a.refund_order_id = c.refund_order_id {condition} GROUP BY a.refund_order_id) AS order_table "
        row = self.db.fetch_one_row(sql_count,params)
        
        return ret_list,row["order_count"]
    
    def get_refund_order_excel_page_list(self, page_index, page_size, where='', params=None):
        """
        :description: 退款订单列表(导出)
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" where {where}"


        sql = f"SELECT a.order_id,a.refund_order_id,a.add_time refund_time,a.user_code,c.goods_name,c.sku_name,d.buy_count,d.price,d.real_pay_price,b.add_time order_time,b.province_name,b.city_name,b.district_name,b.consignee,b.phone,b.address_info,IF(b.logistics_number = '',0,1) AS logistics_status,a.status,a.refund_type,a.reason FROM order_refund_tb a RIGHT JOIN order_tb b ON a.order_id = b.order_id RIGHT JOIN order_refund_goods_tb c ON a.refund_order_id = c.refund_order_id JOIN order_goods_tb d ON c.order_id = d.order_id AND c.goods_id = d.goods_id AND c.sku_id = d.sku_id {condition} ORDER BY a.add_time desc {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT  count(*) as order_count FROM order_refund_tb a RIGHT JOIN order_tb b ON a.order_id = b.order_id RIGHT JOIN order_refund_goods_tb c ON a.refund_order_id = c.refund_order_id JOIN order_goods_tb d ON c.order_id = d.order_id AND c.goods_id = d.goods_id AND c.sku_id = d.sku_id {condition}"
        row = self.db.fetch_one_row(sql_count,params)
        
        return ret_list,row["order_count"]


    def check_refund_complete(self,order_id):
        """
        :description: 判断订单所有的商品是否全部退款完成(成功)
        :last_editors: KangWenBin
        """
        ret = False
        # 订单购买商品
        order_goods_count = OrderGoodsModel(context=self).get_total(where="order_id = %s", params=[order_id])
        # 已完成退款单商品
        sql = "SELECT COUNT(*) as count FROM order_refund_tb a JOIN order_refund_goods_tb b ON a.refund_order_id = b.refund_order_id WHERE b.order_id = %s AND a.status = 5"
        order_refund_goods_count = self.db.fetch_one_row(sql,order_id)["count"]
        if order_goods_count == order_refund_goods_count:
            ret = True
        return ret