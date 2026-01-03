
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class GoodsSkuModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(GoodsSkuModel, self).__init__(GoodsSku, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class GoodsSku:

    def __init__(self):
        super(GoodsSku, self).__init__()
        self.id = 0  # 
        self.goods_id = 0  # 商品id
        self.sku_name = ""  # sku组合名称
        self.sku_picture = ""  # sku图片
        self.sku_info = ""  # sku信息
        self.original_price = 0  # 划线价
        self.price = 0  # 价格
        self.integral = 0  # 积分
        self.goods_code = ""  # 商家编码
        self.add_time = 0  # 创建时间
        self.status = 0  # 1 正常 0 伪删除

    @classmethod
    def get_field_list(self):
        return ['id', 'goods_id', 'sku_name', 'sku_picture', 'sku_info', 'original_price', 'price', 'integral', 'goods_code', 'add_time', 'status']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "goods_sku_tb"
    