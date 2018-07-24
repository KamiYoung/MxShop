"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
import xadmin
from MxShop.settings import MEDIA_ROOT
from django.views.static import serve
from django.urls import include
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from goods.views import GoodsListViewSet

router = DefaultRouter()
# 配置goods的url
router.register(r'goods', GoodsListViewSet)

# 这种绑定可以由router来完成
# goods_list = GoodsListViewSet.as_view({
#     # 将get请求绑定list函数
#     'get': 'list'
# })


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^ueditor/', include(("DjangoUeditor.urls", "ueditor"), namespace="ueditor")),

    # 商品列表页面,url中最好是名次，复数
    # url(r"goods/$", goods_list, name="goods-list"),
    # 使用router来注册url
    url(r'^', include(router.urls)),
    url(r"docs/", include_docs_urls(title="生鲜电商"))
]
