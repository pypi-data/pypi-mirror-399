
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ShopModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(ShopModel, self).__init__(Shop, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Shop:

    def __init__(self):
        super(Shop, self).__init__()
        self.id = 0  # 
        self.wait_pay_time = 0  # 待付款订单自动取消时间(分钟)
        self.logistics_time = 0  # 订单发货截止时间(天) 0 不限制 
        self.auto_receipt_time = 0  # 发货后自动确认时间(天) 0 不操作
        self.consignee = ""  # 收件人
        self.phone = ""  # 电话
        self.address_info = ""  # 退货地址
        self.refund_time = 0  # 退货有效期(超过特定时间未填写退货单号，则自动取消退货申请)
        self.refund_audit = 0  # 退款预计审核时间(小时)
        self.postage_type = 0  # 邮费类型 0 统一配置 1 指定配送区域不包邮
        self.postage = 0  # 邮费
        self.shipping_method = ""  # 配送方式
        self.remark = ""  # 备注说明
        self.coupon_remark = ""  # 优惠券使用说明
        self.status = 0  # 店铺状态 0 下架 1 正常

    @classmethod
    def get_field_list(self):
        return ['id', 'wait_pay_time', 'logistics_time', 'auto_receipt_time', 'consignee', 'phone', 'address_info', 'refund_time', 'refund_audit', 'postage_type', 'postage', 'shipping_method', 'remark', 'coupon_remark', 'status']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "shop_tb"
    