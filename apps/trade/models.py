from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

from goods.models import Goods

user = get_user_model()
# Create your models here.


class ShoppingCart(models.Model):
    '''
    购物车
    '''
    user = models.ForeignKey(user, verbose_name=u'用户')
    goods = models.ForeignKey(Goods, verbose_name=u'商品')
    goods_num = models.IntegerField(default=0, verbose_name="购买数量")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "商品类别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class OrderInfo(models.Model):
    '''
    订单
    '''
    ORDER_STATUS = (
        ("success", "成功"),
        ("cancel", "取消"),
        ("", "待支付")
    )

    user = models.ForeignKey(User, verbose_name=u'用户')
    order_sn = models.CharField(max_length=30, unique=True, verbose_name="订单号")
    trade_no = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"")
    pay_status = models.CharField(choices=ORDER_STATUS, max_length=10, verbose_name="订单支付状态")
    post_script = models.CharField(max_length=11, verbose_name="订单留言")
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    # 用户信息
    address = models.CharField(max_length=100, default="", verbose_name="收货地址")
    singer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    singer_mobile = models.CharField(max_length=11, verbose_name="联系电话")

    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)


class OrderGoods(models.Model):
    '''
    订单商品详情
    '''
    order = models.ForeignKey(OrderInfo, verbose_name="订单信息")
    goods = models.ForeignKey(Goods, verbose_name="商品")
    goods_num = models.IntegerField(default=0, verbose_name="商品数量")

    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"订单商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order.order_sn)

























