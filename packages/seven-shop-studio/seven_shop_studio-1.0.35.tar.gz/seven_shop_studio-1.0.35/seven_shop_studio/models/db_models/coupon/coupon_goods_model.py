
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CouponGoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(CouponGoodsModel, self).__init__(CouponGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class CouponGoods:

    def __init__(self):
        super(CouponGoods, self).__init__()
        self.id = 0  # 
        self.coupon_id = 0  # 优惠券id
        self.goods_id = 0  # 商品id

    @classmethod
    def get_field_list(self):
        return ['id', 'coupon_id', 'goods_id']
        
    @classmethod
    def get_primary_key(self):
        return ""

    def __str__(self):
        return "coupon_goods_tb"
    