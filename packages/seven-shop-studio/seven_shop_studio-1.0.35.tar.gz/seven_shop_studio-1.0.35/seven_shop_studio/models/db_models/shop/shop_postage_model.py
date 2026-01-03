
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ShopPostageModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(ShopPostageModel, self).__init__(ShopPostage, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ShopPostage:

    def __init__(self):
        super(ShopPostage, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.province_name = ""  # 省份
        self.postage = 0  # 邮费

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'province_name', 'postage']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "shop_postage_tb"
    