"""vehicle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('work/', views.work),
    path('about/', views.about),
    path('contact/', views.contact),
    path('work/rules/', views.rules),
    path('work/rules/uniqueid', views.uniqueid),
    path('parse/', views.parse),
    path('parse/sequence/', views._parse_sequence),
    path('parse/datafield/', views._parse_datafield),
    path('detect/', views.detect),
    path('detect/sequence', views._detect_sequence),
    path('detect/sequenceRelationship', views._detect_sequenceRelationship),
    path('detect/datafield', views._detect_datafield),
    path('detect/datafieldRelationship', views._detect_datafieldRelationship),



    path('construct/', views.construct),
    path('construct/insert', views._construct_insert),
    path('construct/erase', views._construct_erase),
    path('construct/reput', views._construct_reput),
    path('construct/changeDataField', views._construct_changeDataField),
    path('construct/about', views._construct_about),

    path('construct/construct_reput_single', views._construct_reput_single),
    path('construct/construct_reput_all', views._construct_reput_all),
    # 构建完成页面后，需要再实现一个展示系统，展示我们的攻击数据，并且为将来的操作打下基础
    # 每次攻击后，生成的数据都应当只有一个文件吧？
    path('erase_attack', views.erase_attack),
    path('insert_attack', views.insert_attack),
    path('reput_attack', views.reput_attack),
    path('changeDataField_attack', views.changeDataField_attack),

    # url:"/attack_make",
    path('attack_make', views.attack_make),
]
