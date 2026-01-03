# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:36
:LastEditTime: 2025-02-19 13:56:28
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class OrderModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(OrderModel, self).__init__(Order, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Order:

    def __init__(self):
        super(Order, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.order_id = ""  # 订单号
        self.pay_channel = 0  # 支付渠道 0 微信小程序
        self.channel_id = 0  # 订单来源 1 商品页 2 购物车
        self.pay_order_id = ""  # 支付平台订单id
        self.user_code = ""  # 购买用户id
        self.act_id = "" # 活动id
        self.open_id = ""  # open_id
        self.province_name = ""  # 省
        self.city_name = ""  # 市
        self.district_name = ""  # 县、区
        self.consignee = ""  # 收货人
        self.phone = ""  # 电话
        self.address_info = ""  # 详细地址
        self.buy_count = 0  # 订单购买总数量
        self.price = 0  # 订单商品总价
        self.real_pay_price = 0  # 实际支付价格
        self.postage = 0  # 运费
        self.coupon_id = 0  # 优惠券id
        self.coupon_price = 0  # 优惠金额
        self.add_time = 0  # 下单时间
        self.pay_time = 0  # 支付时间
        self.status = 0  # 状态 0 未支付 1 已取消 2 已支付(待发货) 3 已发货 4 已完成 5 不予发货
        self.logistics_company = ""  # 物流公司
        self.logistics_number = ""  # 物流单号
        self.logistics_time = 0  # 发货时间
        self.finish_time = 0  # 完成时间
        self.remark = ""  # 买家备注
        self.shop_remark = ""  # 卖家备注
        self.cancel_remark = ""  # 取消备注
        self.is_refund = 0  # 是否退款 0 否 1 是
        self.is_complete = 0 # 订单是否完成 0 否 1 是
        self.sync_status = 0  # 订单同步状态，用于逅甲或者ERP同步订单 (0未同步，1同步成功，2同步失败)
        self.sync_date = 0  # 同步时间
        self.sync_count = 0 # 同步次数
        self.sync_result = "" # 同步结果
        self.wx_sync_status = 0  # 微信订单同步状态(0未同步，1同步成功，2同步失败)
        self.wx_sync_date = 0  # 微信同步时间
        self.wx_sync_result = "" # 微信同步结果
        
        

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'order_id', 'pay_channel', 'channel_id', 'pay_order_id', 'user_code', 'act_id', 'open_id', 'province_name', 'city_name', 'district_name', 'consignee', 'phone', 'address_info', 'buy_count', 'price', 'real_pay_price', 'postage', 'coupon_id', 'coupon_price', 'add_time', 'pay_time', 'status', 'logistics_company', 'logistics_number', 'logistics_time', 'finish_time', 'remark', 'shop_remark', 'cancel_remark', 'is_refund', 'is_complete', 'sync_status', 'sync_date', 'sync_count', 'sync_result', 'wx_sync_status', 'wx_sync_date', 'wx_sync_result']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "order_tb"
    