
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class GoodsRecommendModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(GoodsRecommendModel, self).__init__(GoodsRecommend, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class GoodsRecommend:

    def __init__(self):
        super(GoodsRecommend, self).__init__()
        self.id = 0  # 
        self.goods_id = 0  # 商品id
        self.sort = 0  # 排序
        self.add_time = 0  # 添加时间

    @classmethod
    def get_field_list(self):
        return ['id', 'goods_id', 'sort', 'add_time']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "goods_recommend_tb"
    