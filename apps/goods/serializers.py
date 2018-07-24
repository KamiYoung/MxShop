from rest_framework import serializers

from goods.models import Goods, GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsSerializer(serializers.ModelSerializer):
    """
    直接通过models来读取字段，精简属性
    """
    category = CategorySerializer()

    class Meta:
        model = Goods
        # 如果需要所有属性，那么使用all
        fields = "__all__"
        # 如果需要特定几个列，那么使用一下格式
        # fields = ("name", "click_num", "market_price", "add_time")
        # 如果需要排除特定列，使用exclude

