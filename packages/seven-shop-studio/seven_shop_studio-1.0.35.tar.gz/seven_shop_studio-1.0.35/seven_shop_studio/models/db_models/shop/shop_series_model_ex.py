from seven_shop_studio.models.db_models.shop.shop_series_model import *

class ShopSeriesModelEx(ShopSeriesModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)
    
    def get_category_series_count(self,category_id):
        """
        :description: 获取分类对应系列数量
        :last_editors: KangWenBin
        """        
        sql = "select count(*) as goods_count from shop_category_series_tb a join shop_series_tb b on a.series_id = b.id where b.status>-1 and a.category_id = %s"
        return self.db.fetch_one_row(sql,category_id)["goods_count"]
    
    def get_series_category_list(self,series_id):
        """
        :description: 获取系列对应分类
        :last_editors: KangWenBin
        """        
        sql = "SELECT b.id,b.category_name FROM shop_category_series_tb a JOIN shop_category_tb b ON a.category_id = b.id WHERE a.series_id = %s AND b.status>-1"
        return self.db.fetch_all_rows(sql,series_id)