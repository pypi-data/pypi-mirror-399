# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-27 15:36:11
:LastEditTime: 2024-06-19 14:46:05
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.coupon.coupon_grant_model import *

class CouponGrantModelEx(CouponGrantModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_grant_list(self, page_index, page_size, where='', params=None):
        """
        :description: 投放列表
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" where {where}"

        sql = f"SELECT a.id,a.grant_name,a.grant_type,a.grant_picture,a.begin_time,a.end_time,a.status AS grant_status,a.add_time,b.coupon_name,b.status AS coupon_status,b.coupon_type FROM coupon_grant_tb a LEFT JOIN coupon_tb b ON a.coupon_id = b.id {condition} ORDER BY id desc {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT count(*) as count FROM coupon_grant_tb a LEFT JOIN coupon_tb b ON a.coupon_id = b.id {condition} " 
        row = self.db.fetch_one_row(sql_count,params)
        return ret_list,row["count"]
    