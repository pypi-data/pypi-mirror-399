
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ShopSeriesModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(ShopSeriesModel, self).__init__(ShopSeries, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ShopSeries:

    def __init__(self):
        super(ShopSeries, self).__init__()
        self.id = 0  # 
        self.sort = 0  # 排序
        self.shop_id = 0  # 店铺id
        self.series_name = ""  # 系列名称
        self.series_picture = ""  # 系列头图
        self.series_poster = ""  # 系列海报
        self.status = 0  # 状态 0 未发布 1 已发布 -1 伪删除
        self.add_time = 0  # 添加时间

    @classmethod
    def get_field_list(self):
        return ['id', 'sort', 'shop_id', 'series_name', 'series_picture', 'series_poster', 'status', 'add_time']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "shop_series_tb"
    