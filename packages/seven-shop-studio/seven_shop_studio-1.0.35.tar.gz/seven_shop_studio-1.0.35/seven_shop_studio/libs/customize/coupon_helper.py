from seven_shop_studio.models.db_models.order.order_refund_model_ex import *
from seven_shop_studio.models.db_models.coupon.coupon_record_model import *

class CouponHelper(object):
    @classmethod
    def refund_coupon_check(self, coupon_id, order_id):
        """
        :description: 检测优惠券是否可退
        :last_editors: KangWenBin
        """        
        if coupon_id > 0:
            if OrderRefundModelEx(context=self).check_refund_complete(order_id):
                # 退还优惠券
                CouponRecordModel(context=self).update_table("order_id = '',use_time = 0,status = 0","id = %s",coupon_id)
