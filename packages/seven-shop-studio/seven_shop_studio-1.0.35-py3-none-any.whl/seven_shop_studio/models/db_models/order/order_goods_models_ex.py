# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-22 16:19:34
:LastEditTime: 2024-07-16 11:54:13
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.order.order_goods_model import *

class OrderGoodsModelEx(OrderGoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)


    def get_order_goods_list(self,order_id_list):
        """
        :description: 获取订单商品相关信息
        :last_editors: Kangwenbin
        """
        
        sql = "SELECT a.order_id,a.goods_id,a.sku_id,a.sku_name,a.goods_picture,a.goods_name,a.buy_count,a.price,a.real_pay_price,c.status as refund_status FROM order_goods_tb a LEFT JOIN order_refund_goods_tb b ON a.order_id = b.order_id AND a.goods_id = b.goods_id AND a.sku_id = b.sku_id LEFT JOIN order_refund_tb c ON b.refund_order_id = c.refund_order_id where a.order_id in %s"
        goods_list = self.db.fetch_all_rows(sql, (order_id_list,))
        # 数据处理(去重)
        unique_data = {}
        for item in goods_list:
            order_id = item['order_id']
            goods_id = item['goods_id']
            sku_id = item['sku_id']
            # 检查当前的goods_id和sku_id组合是否已经存在于字典中
            if (order_id, goods_id, sku_id) not in unique_data or unique_data[(order_id, goods_id, sku_id)]['refund_status'] == 4:
                # 如果不存在或者refund_status为4，则更新字典
                unique_data[(order_id, goods_id, sku_id)] = item

        # 将字典转换回列表形式，如果需要
        goods_list = list(unique_data.values())
        return goods_list