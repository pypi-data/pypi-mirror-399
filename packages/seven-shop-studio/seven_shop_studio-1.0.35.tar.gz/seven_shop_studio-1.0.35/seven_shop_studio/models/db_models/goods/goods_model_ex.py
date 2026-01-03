# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:35
:LastEditTime: 2024-07-16 11:59:42
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.goods.goods_model import *


class GoodsModelEx(GoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_goods_list(self,page_index,page_size,where='',order_by='',params=None):
        """
        :description: 商品列表
        :last_editors: KangWenBin
        """        
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"

        condition = ""
        if where:
            condition += f" and {where}"

        sql = f"SELECT a.id,a.sort,a.goods_main_images as goods_picture,a.goods_short_name,a.series_id,ifnull(d.series_name,'') as series_name,a.goods_sold,SUM(c.inventory) AS inventory,a.status,a.add_time FROM goods_tb a LEFT JOIN goods_sku_tb b ON a.id = b.goods_id LEFT JOIN inventory_tb c ON a.id = c.goods_id AND (b.id = c.sku_id OR (b.id IS NULL AND c.sku_id = 0)) left join shop_series_tb d on a.series_id = d.id  WHERE (b.status = 1 OR b.status IS NULL) {condition} GROUP BY a.id ORDER BY {order_by} {limit}"

        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT count(*) as count FROM goods_tb a LEFT JOIN goods_sku_tb b ON a.id = b.goods_id LEFT JOIN inventory_tb c ON a.id = c.goods_id AND (b.id = c.sku_id OR (b.id IS NULL AND c.sku_id = 0)) left join shop_series_tb d on a.series_id = d.id WHERE (b.status = 1 OR b.status IS NULL) {condition} GROUP BY a.id" 
        row = self.db.get_row_count(sql_count,params)
        return ret_list,row

    def get_goods_recommend_list(self,page_index,page_size,where='',order_by='',params=None):
        """
        :description: 推荐商品列表
        :last_editors: KangWenBin
        """
        limit = f"LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"
        condition = ""
        if where:
            condition += f" where {where}"
        if order_by:
            order_by = f" order by {order_by}"
        sql = f"SELECT a.sort,a.goods_id,b.goods_short_name as goods_name,b.goods_main_images as goods_picture,b.series_id,c.series_name,b.status,a.add_time FROM goods_recommend_tb a JOIN goods_tb b ON a.goods_id = b.id JOIN shop_series_tb c ON c.id = b.series_id {condition} {order_by} {limit}"
        ret_list = self.db.fetch_all_rows(sql,params)
        sql_count = f"SELECT count(*) as count FROM goods_recommend_tb a JOIN goods_tb b ON a.goods_id = b.id JOIN shop_series_tb c ON c.id = b.series_id {condition}" 
        row = self.db.fetch_one_row(sql_count,params)["count"]
        return ret_list,row
    
    def get_recommend_sort(self):
        sort = 0
        