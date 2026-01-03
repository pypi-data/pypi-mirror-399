# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:36
:LastEditTime: 2024-07-10 14:22:41
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.order.order_model import *


class OrderModelEx(OrderModel):
    
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_order_page_list(self, page_index, page_size, where='', params=None):
        """
        :description: 订单列表
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" where {where}"


        sql = f"SELECT a.user_code,a.order_id,a.add_time,a.real_pay_price,a.remark,a.shop_remark,a.status,a.province_name,a.city_name,a.district_name,a.consignee,a.phone,a.address_info,a.logistics_company,a.logistics_number FROM order_tb a left JOIN order_goods_tb b ON a.order_id = b.order_id {condition} group by a.order_id order by a.add_time desc {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT COUNT(*) as order_count FROM (SELECT a.order_id FROM order_tb a LEFT JOIN order_goods_tb b ON a.order_id = b.order_id {condition} GROUP BY a.order_id) AS order_table "
        row = self.db.fetch_one_row(sql_count,params)
        
        return ret_list,row["order_count"]
    
    def get_order_excel_page_list(self, page_index, page_size, where='', params=None):
        """
        :description: 订单导出列表
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" where {where}"


        sql = f"SELECT a.order_id,a.user_code,b.goods_name,b.sku_name,b.buy_count,b.price,b.real_pay_price,a.add_time,a.status,a.province_name,a.city_name,a.district_name,a.consignee,a.phone,a.address_info,a.logistics_company,a.logistics_number,a.logistics_time,d.status AS refund_status FROM order_tb a LEFT JOIN order_goods_tb b ON a.order_id = b.order_id LEFT JOIN order_refund_goods_tb c ON b.order_id = c.order_id AND b.goods_id = c.goods_id AND b.sku_id = c.sku_id LEFT JOIN order_refund_tb d ON c.refund_order_id = d.refund_order_id {condition} order by a.add_time desc {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT count(*) as order_count FROM order_tb a LEFT JOIN order_goods_tb b ON a.order_id = b.order_id LEFT JOIN order_refund_goods_tb c ON b.order_id = c.order_id AND b.goods_id = c.goods_id AND b.sku_id = c.sku_id LEFT JOIN order_refund_tb d ON c.refund_order_id = d.refund_order_id {condition} "
        row = self.db.fetch_one_row(sql_count,params)
        
        return ret_list,row["order_count"]