# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-20 19:18:27
:LastEditTime: 2024-06-20 19:31:13
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.coupon.coupon_model import *
from seven_shop_studio.models.db_models.coupon.coupon_record_model import *

class CouponModelEx(CouponModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def update_coupon_inventory(self,coupon_id):
        """
        :description: 修改优惠券库存
        :last_editors: KangWenBin
        """        
        sql = "UPDATE coupon_tb SET record_number = IF(record_number + 1 > coupon_inventory, record_number, record_number + 1) WHERE id = %s"
        row_count = self.db.update(sql,coupon_id)
        return row_count
    
    def check_coupon_inventory(self,coupon_id):
        """
        :description: 检查优惠券库存是否正确
        :last_editors: KangWenBin
        """
        inventory_model = self.get_dict(where="id = %s",params=[coupon_id],field="record_number")
        record_number = CouponRecordModel(context=self).get_total(where="coupon_id = %s",params=[coupon_id])
        if not inventory_model:
            return
            
        if inventory_model["record_number"] != record_number:
            self.update_table(update_sql="record_number = %s",where="id = %s",params=[record_number,coupon_id])
    