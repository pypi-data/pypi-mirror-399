# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2022-11-21 17:46:56
:LastEditTime: 2024-06-19 14:43:24
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop_studio.handlers.server.shop import *
from seven_shop_studio.handlers.server.category import *
from seven_shop_studio.handlers.server.series import *
from seven_shop_studio.handlers.server.order import *
from seven_shop_studio.handlers.server.goods import *
from seven_shop_studio.handlers.server.coupon import *


def seven_shop_studio_route():
    return [
        # 店铺
            (r"/server/shop/info", ShopInfoHandler), # 店铺信息

            # 分类
            (r"/server/category/info", CategoryInfoHandler), # 分类保存/分类上下架 
            (r"/server/category/list", CategoryListHandler), # 分类列表 
            
            # 系列
            (r"/server/series/info", SeriesInfoHandler), # 系列保存/系列上下架
            (r"/server/series/list", SeriesListHandler), # 系列列表 
            
            # 订单
            (r"/server/order/list", OrderListHandler), # 订单列表
            (r"/server/order/info", OrderInfoHandler), # 订单
            (r"/server/refund/list", RefundOrderListHandler), # 退款订单列表
            (r"/server/refund/info", RefundOrderInfoHandler), # 退款订单操作
            (r"/server/refund/notify", RefundNotifyHandler), # 微信退款回调

            # 商品
            (r"/server/goods/list", GoodsListHandler), # 商品列表
            (r"/server/goods/info", GoodsInfoHandler), # 商品信息
            (r"/server/goods/recommend", GoodsRecommendListHandler), # 推荐商品信息
            
            # 优惠券
            (r"/server/coupon/list", CouponListHandler), # 优惠券列表
            (r"/server/coupon/info", CouponInfoHandler), # 优惠券信息
            (r"/server/grant/list", CouponGrantListHandler), # 优惠券投放列表
            (r"/server/grant/info", CouponGrantInfoHandler), # 优惠券投放详情
            (r"/server/coupon/record", CouponRecordListHandler), # 优惠券领取记录
            (r"/server/coupon/user", CouponUserListHandler), # 用户优惠券
            
    ]
