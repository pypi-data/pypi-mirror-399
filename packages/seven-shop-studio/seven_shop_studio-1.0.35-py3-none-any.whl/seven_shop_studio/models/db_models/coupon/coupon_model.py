
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CouponModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(CouponModel, self).__init__(Coupon, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Coupon:

    def __init__(self):
        super(Coupon, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.coupon_name = ""  # 优惠券名称
        self.coupon_type = 0  # 优惠券类型 0 满减券 1 折扣券
        self.use_price = 0  # 使用条件金额
        self.coupon_price = 0  # 优惠金额
        self.coupon_discount = 0  # 优惠折扣
        self.goods_limit = 0  # 使用限制 0 关闭 1 开启
        self.coupon_inventory = 0  # 优惠券数量
        self.record_number = 0  # 领取数量
        self.begin_time = 0  # 有效期_开始时间
        self.end_time = 0  # 有效期_结束时间
        self.using_rule = ""  # 使用规则
        self.add_time = 0  # 添加时间
        self.is_receive = 0  # 是否可以领取 0 否 1 是
        self.status = 0  # 优惠券状态 0 未发布 1 已发布 -1 伪删除

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'coupon_name', 'coupon_type', 'use_price', 'coupon_price', 'coupon_discount', 'goods_limit', 'coupon_inventory', 'record_number', 'begin_time', 'end_time', 'using_rule', 'add_time', 'is_receive', 'status']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "coupon_tb"
    