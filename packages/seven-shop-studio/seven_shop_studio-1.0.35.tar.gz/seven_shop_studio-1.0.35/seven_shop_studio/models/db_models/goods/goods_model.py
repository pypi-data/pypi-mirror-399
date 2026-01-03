# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-19 14:48:35
:LastEditTime: 2024-08-01 10:10:52
:LastEditors: KangWenBin
:Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class GoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super(GoodsModel, self).__init__(Goods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class Goods:

    def __init__(self):
        super(Goods, self).__init__()
        self.id = 0  # 
        self.shop_id = 0  # 店铺id
        self.series_id = 0  # 系列id
        self.goods_main_images = ""  # 商品主图(多张)
        self.goods_detail_images = ""  # 商品详情图(多张)
        self.goods_tag_image = "" # 商品标签图
        self.goods_long_name = ""  # 商品长名称
        self.goods_short_name = ""  # 商品短名称
        self.goods_remark = ""  # 商品备注
        self.goods_parameter = ""  # 商品参数
        self.goods_service = ""  # 商品服务条款
        self.goods_sold = 0  # 商品销量
        self.original_price = 0  # 原价
        self.price = 0  # 价格
        self.integral = 0  # 积分
        self.goods_code = ""  # 商家编码
        self.is_integral = 0  # 是否积分商品 0 否 1 是
        self.sort = 0  # 商品排序
        self.status = 0  # 状态 0 未上架 1 已上架 -1 伪删除
        self.add_time = 0  # 添加时间

    @classmethod
    def get_field_list(self):
        return ['id', 'shop_id', 'series_id', 'goods_main_images', 'goods_detail_images', 'goods_tag_image', 'goods_long_name', 'goods_short_name', 'goods_remark', 'goods_parameter', 'goods_service', 'goods_sold', 'original_price', 'price', 'integral', 'goods_code', 'is_integral', 'sort', 'status', 'add_time']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "goods_tb"
    