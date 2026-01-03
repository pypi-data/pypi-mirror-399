
"""
:Author: KangWenBin
:Date: 2024-05-17 15:57:20
:LastEditTime: 2024-05-17 17:29:38
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.models.db_models.goods.goods_sku_model import *


class GoodsSkuModelEx(GoodsSkuModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_goods_sku_list(self,goods_id):
        """
        :description: 获取商品sku信息
        :last_editors: KangWenBin
        """
        sql = "SELECT a.id,a.goods_code,a.sku_picture,a.sku_name,a.price,b.inventory FROM goods_sku_tb a JOIN inventory_tb b ON a.goods_id = b.goods_id AND a.id = b.sku_id WHERE a.status > -1 and a.goods_id = %s"
        return self.db.fetch_all_rows(sql,goods_id)

    def get_goods_sku_info(self, goods_id):
        """
        :description: 获取商品sku信息
        :param goods_id 商品id
        :last_editors: Kangwenbin
        """        
        ret_model = {
            "sku_list": [],
            "sku_model": {}
        }
        sql = "SELECT a.*,b.inventory FROM goods_sku_tb a JOIN inventory_tb b ON a.goods_id = b.goods_id AND a.id = b.sku_id WHERE a.status > -1 AND a.goods_id = %s"
        goods_sku_list= self.db.fetch_all_rows(sql,goods_id)
        if goods_sku_list:
            # sku信息处理
            for item in goods_sku_list:
                # 不存在sku细项则跳过
                if not item["sku_info"]:
                    continue

                json_sku_list = json.loads(item["sku_info"])
                # 选择项处理
                for sku in json_sku_list:
                    if sku["model_name"] not in ret_model["sku_model"]:
                        ret_model["sku_model"][sku["model_name"]] = []

                    if sku["model_value"] not in ret_model["sku_model"][sku["model_name"]]:
                        ret_model["sku_model"][sku["model_name"]].append(sku["model_value"])

                sku_model = {
                    "sku_name": item["sku_name"],
                    "id": item["id"],
                    "price": item["price"],
                    "original_price":item["original_price"],
                    "integral":item["integral"],
                    "sku_picture": item["sku_picture"],
                    "goods_code": item["goods_code"],
                    "inventory": item["inventory"]
                }
                ret_model["sku_list"].append(sku_model)
                
        return ret_model