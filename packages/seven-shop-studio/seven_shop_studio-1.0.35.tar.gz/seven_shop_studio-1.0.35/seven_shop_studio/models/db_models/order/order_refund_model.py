# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:36
:LastEditTime: 2024-07-19 16:14:06
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class OrderRefundModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(OrderRefundModel, self).__init__(OrderRefund, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class OrderRefund:

    def __init__(self):
        super(OrderRefund, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.order_id = ""  # 订单号
        self.refund_order_id = ""  # 退款订单号
        self.refund_type = 0  # 退款类型 0 退货退款 1 仅退款
        self.goods_refund_price = 0  # 商品退款金额
        self.real_refund_price = 0  # 实际退款金额
        self.postage = 0  # 运费
        self.reason = ""  # 退款理由
        self.status = 0  # 状态 0 提交申请 1 通过 2 拒绝 3 商品寄回中 4 撤销 5 完成 6 失败
        self.refund_status = ""  # 微信退款平台状态
        self.refund_pay_id = ""  # 支付平台退款单号
        self.address_info = ""  # 售后地址
        self.logistics_company = ""  # 物流公司
        self.logistics_number = ""  # 退货物流单号
        self.add_time = 0  # 申请时间
        self.pass_time = 0  # 审核时间
        self.logistics_time = 0  # 用户发货时间
        self.receive_time = 0  # 商家收货时间
        self.finish_time = 0  # 结束时间
        self.user_code = ""  # 添加人id
        self.act_id = ""  # 活动id
        self.manage_user = ""  # 管理人id
        self.pass_remark = ""  # 审核备注
        self.fail_remark = ""  # 订单失败备注
        self.sync_status = 0  # 订单同步状态，用于逅甲或者ERP同步订单 (0未同步，1同步成功，2同步失败)
        self.sync_date = 0  # 同步时间
        self.sync_count = 0 # 同步次数
        self.sync_result = "" # 同步结果

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'order_id', 'refund_order_id', 'refund_type', 'goods_refund_price', 'real_refund_price', 'postage', 'reason', 'status', 'refund_status', 'refund_pay_id', 'address_info', 'logistics_company', 'logistics_number', 'add_time', 'pass_time', 'logistics_time', 'receive_time', 'finish_time', 'user_code', 'act_id', 'manage_user', 'pass_remark', 'fail_remark', 'sync_status', 'sync_date', 'sync_count', 'sync_result']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "order_refund_tb"
    