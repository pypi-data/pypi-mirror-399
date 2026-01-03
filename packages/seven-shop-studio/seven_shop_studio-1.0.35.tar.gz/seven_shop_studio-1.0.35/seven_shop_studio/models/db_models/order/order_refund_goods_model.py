
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class OrderRefundGoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(OrderRefundGoodsModel, self).__init__(OrderRefundGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class OrderRefundGoods:

    def __init__(self):
        super(OrderRefundGoods, self).__init__()
        self.id = 0  # 
        self.order_id = ""  # 关联下单号
        self.refund_order_id = ""  # 关联退款单号
        self.goods_id = 0  # 商品id
        self.sku_id = 0  # sku_id
        self.sku_name = ""  # sku名称
        self.goods_name = ""  # 商品名称
        self.goods_picture = ""  # 商品图片
        self.refund_count = 0  # 退款数量
        self.refund_price = 0  # 退款金额
        self.add_time = 0  # 创建时间
        self.goods_code = ""  # 商家编码

    @classmethod
    def get_field_list(self):
        return ['id', 'order_id', 'refund_order_id', 'goods_id', 'sku_id', 'sku_name', 'goods_name', 'goods_picture', 'refund_count', 'refund_price', 'add_time', 'goods_code']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "order_refund_goods_tb"
    