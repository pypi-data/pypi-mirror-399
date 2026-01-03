
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ShopCategoryModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(ShopCategoryModel, self).__init__(ShopCategory, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ShopCategory:

    def __init__(self):
        super(ShopCategory, self).__init__()
        self.id = 0  # 
        self.category_name = ""  # 分类名称
        self.sort = 0  # 分类排序
        self.shop_id = 0  # 店铺id
        self.status = 0  # 分类状态 0 未发布 1 发布 -1 伪删除
        self.add_time = 0  # 添加时间

    @classmethod
    def get_field_list(self):
        return ['id', 'category_name', 'sort', 'shop_id', 'status', 'add_time']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "shop_category_tb"
    