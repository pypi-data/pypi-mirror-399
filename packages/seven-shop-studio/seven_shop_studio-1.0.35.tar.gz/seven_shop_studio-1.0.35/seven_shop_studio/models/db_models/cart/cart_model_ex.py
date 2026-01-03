# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-21 11:29:36
:LastEditTime: 2024-07-17 13:42:52
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.cart.cart_model import *


class CartModelEx(CartModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)
    
    def get_cart_list(self, shop_id, act_id, begin_time, end_time):
        """
        :description: 获取时间段内购物车列表
        :last_editors: KangWenBin
        """
        sql = "SELECT a.user_code,a.buy_count,a.add_time FROM cart_tb a JOIN goods_tb b ON a.goods_id = b.id WHERE b.shop_id = %s and act_id = %s and a.add_time >= %s and a.add_time < %s"
        params = (shop_id, act_id, begin_time, end_time)
        return self.db.fetch_all_rows(sql, params)