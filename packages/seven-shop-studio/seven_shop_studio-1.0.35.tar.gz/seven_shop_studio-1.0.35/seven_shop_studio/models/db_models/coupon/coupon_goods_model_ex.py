# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-24 18:03:11
:LastEditTime: 2024-05-24 18:12:41
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop_studio.models.db_models.coupon.coupon_goods_model import *

class CouponGoodsModelEx(CouponGoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_coupon_goods_list(self, coupon_id):
        """
        :description: 获取优惠券商品列表
        :last_editors: KangWenBin
        """        
        sql = "select a.goods_short_name,a.goods_main_images as goods_picture,b.goods_id from goods_tb a join coupon_goods_tb b on a.id=b.goods_id where a.status = 1 and b.coupon_id=%s"
        params = [coupon_id]
        goods_list = self.db.fetch_all_rows(sql, params)
        # 处理商品图片
        for item in goods_list:
            try:
                item["goods_picture"] = json.loads(item["goods_picture"])[0]
            except:
                item["goods_picture"] = ""
        return goods_list