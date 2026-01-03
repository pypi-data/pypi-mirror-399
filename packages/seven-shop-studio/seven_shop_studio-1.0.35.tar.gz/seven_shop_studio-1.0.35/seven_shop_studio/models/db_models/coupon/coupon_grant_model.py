
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CouponGrantModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(CouponGrantModel, self).__init__(CouponGrant, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class CouponGrant:

    def __init__(self):
        super(CouponGrant, self).__init__()
        self.id = 0  # 
        self.grant_name = ""  # 投放名称
        self.grant_type = ""  # 投放人群 0 新用户 1 未消费用户 2 已消费用户 3 会员用户
        self.grant_picture = ""  # 投放海报
        self.coupon_id = 0  # 消费券id
        self.begin_time = 0  # 投放开始时间
        self.end_time = 0  # 投放结束时间
        self.add_time = 0  # 创建时间
        self.status = 0  # 状态 0 未发布 1 已发布

    @classmethod
    def get_field_list(self):
        return ['id', 'grant_name', 'grant_type', 'grant_picture', 'coupon_id', 'begin_time', 'end_time', 'add_time', 'status']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "coupon_grant_tb"
    