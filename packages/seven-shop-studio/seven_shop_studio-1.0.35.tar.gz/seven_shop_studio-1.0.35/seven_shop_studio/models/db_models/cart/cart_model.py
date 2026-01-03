
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CartModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(CartModel, self).__init__(Cart, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Cart:

    def __init__(self):
        super(Cart, self).__init__()
        self.id = 0  # 
        self.user_code = ""  # 用户标识
        self.act_id = "" # 活动id
        self.goods_id = 0  # 商品id
        self.sku_id = 0  # sku_id
        self.buy_count = 0  # 购买数量
        self.price = 0  # 添加购物车时价格
        self.add_time = 0  # 添加时间

    @classmethod
    def get_field_list(self):
        return ['id', 'user_code', 'act_id', 'goods_id', 'sku_id', 'buy_count', 'price', 'add_time']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "cart_tb"
    