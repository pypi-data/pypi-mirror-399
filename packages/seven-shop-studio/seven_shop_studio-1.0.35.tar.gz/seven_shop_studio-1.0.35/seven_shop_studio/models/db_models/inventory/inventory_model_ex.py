# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-17 17:33:38
:LastEditTime: 2024-05-17 17:33:54
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.inventory.inventory_model import *
from seven_shop_studio.models.db_models.inventory.inventory_change_model import *


class InventoryModelEx(InventoryModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_inventory(self,goods_id,sku_id):
        """
        :description: 获取库存数量
        :last_editors: KangWenBin
        """        
        inventory = 0
        inventory_model = self.get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        if inventory_model:
            inventory = inventory_model["inventory"]
        return inventory
    

    def check_goods_inventory(self,goods_id,sku_id):
        """
        :description: 单个商品库存验证
        :last_editors: Kangwenbin
        """        
        inventory_model = self.get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        sum_inventory_model = InventoryChangeModel(context=self).get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="IFNULL(sum(change_inventory),0) as change_inventory")
        if not inventory_model or not sum_inventory_model:
            return
        if inventory_model["inventory"] != sum_inventory_model["change_inventory"]:
            self.update_table(update_sql="inventory = %s",where="goods_id = %s and sku_id = %s",params=[sum_inventory_model["change_inventory"],goods_id,sku_id])