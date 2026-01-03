
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class InventoryModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(InventoryModel, self).__init__(Inventory, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Inventory:

    def __init__(self):
        super(Inventory, self).__init__()
        self.id = 0  # 
        self.goods_id = 0  # 商品id
        self.sku_id = 0  # sku_id
        self.inventory = 0  # 库存数

    @classmethod
    def get_field_list(self):
        return ['id', 'goods_id', 'sku_id', 'inventory']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "inventory_tb"
    