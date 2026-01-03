# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:36
:LastEditTime: 2024-07-17 11:37:44
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class OrderGoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(OrderGoodsModel, self).__init__(OrderGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class OrderGoods:

    def __init__(self):
        super(OrderGoods, self).__init__()
        self.id = 0  # 
        self.order_id = ""  # 订单id
        self.goods_id = 0  # 商品id
        self.sku_id = 0  # sku_id
        self.sku_name = ""  # sku_信息
        self.goods_picture = ""  # 商品图片
        self.user_code = ""  # 用户id
        self.act_id = "" # 活动id
        self.goods_name = ""  # 商品名称
        self.buy_count = 0  # 购买数量
        self.price = 0  # 总价
        self.real_pay_price = 0  # 实际支付数
        self.coupon_id = 0  # 优惠券id
        self.coupon_price = 0  # 优惠券金额
        self.add_time = 0  # 添加时间
        self.goods_code = ""  # 商家编码

    @classmethod
    def get_field_list(self):
        return ['id', 'order_id', 'goods_id', 'sku_id', 'sku_name', 'goods_picture', 'user_code', 'act_id', 'goods_name', 'buy_count', 'price', 'real_pay_price', 'coupon_id', 'coupon_price', 'add_time', 'goods_code']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "order_goods_tb"
    