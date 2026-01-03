# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:35
:LastEditTime: 2024-07-17 11:36:30
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CouponRecordModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(CouponRecordModel, self).__init__(CouponRecord, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class CouponRecord:

    def __init__(self):
        super(CouponRecord, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.grant_id = 0  # 投放id
        self.coupon_id = 0  # 优惠券id
        self.coupon_info = ""  # 优惠券领取快照
        self.use_price = 0  # 使用条件金额
        self.goods_limit = 0  # 使用限制 0 关闭 1 开启
        self.goods_list = ""  # 商品列表
        self.begin_time = 0  # 有效时间开始
        self.end_time = 0  # 有效时间结束
        self.user_code = ""  # 用户标识
        self.act_id = "" # 活动id
        self.order_id = ""  # 订单号
        self.add_time = 0  # 领取时间
        self.use_time = 0  # 使用时间
        self.coupon_source = 0  # 0 领取 1 投放 2 发放
        self.status = 0  # 0 未使用 1 已使用

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'grant_id', 'coupon_id', 'coupon_info', 'use_price', 'goods_limit', 'goods_list', 'begin_time', 'end_time', 'user_code', 'act_id', 'order_id', 'add_time', 'use_time', 'coupon_source', 'status']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "coupon_record_tb"
    