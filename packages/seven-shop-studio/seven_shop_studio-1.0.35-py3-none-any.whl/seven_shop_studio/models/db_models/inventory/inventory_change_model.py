# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:36
:LastEditTime: 2024-07-17 11:37:02
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class InventoryChangeModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(InventoryChangeModel, self).__init__(InventoryChange, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class InventoryChange:

    def __init__(self):
        super(InventoryChange, self).__init__()
        self.id = 0  # 
        self.order_id = ""  # 相关联订单id
        self.goods_id = 0  # 商品id
        self.sku_id = 0  # sku_id
        self.change_inventory = 0  # 库存变更数量
        self.add_time = 0  # 添加时间
        self.add_user = 0  # 添加用户
        self.act_id = "" # 活动id
        self.remark = ""  # 备注

    @classmethod
    def get_field_list(self):
        return ['id', 'order_id', 'goods_id', 'sku_id', 'change_inventory', 'add_time', 'add_user', 'act_id', 'remark']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "inventory_change_tb"
    