# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-07-09 17:37:19
:LastEditTime: 2024-07-17 14:05:03
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.goods.goods_recommend_model import *

class GoodsRecommendModelEx(GoodsRecommendModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_recommend_sort(self):
        """
        :description: 获取当前最大排序
        :last_editors: KangWenBin
        """        
        sort = 1
        recommend_model = self.get_dict(order_by='sort desc')
        if recommend_model:
            sort = recommend_model['sort'] + 1
        return sort
        