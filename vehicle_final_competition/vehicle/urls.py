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
    path('parse/lstm', views._parse_lstm),
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
    path('construct/fuzz', views._construct_fuzz),
    # 构建完成页面后，需要再实现一个展示系统，展示我们的攻击数据，并且为将来的操作打下基础
    # 每次攻击后，生成的数据都应当只有一个文件吧？
    path('erase_attack', views.erase_attack),
    path('insert_attack', views.insert_attack),
    path('fuzz_attack', views.fuzz_attack),
    path('reput_attack', views.reput_attack),
    path('changeDataField_attack', views.changeDataField_attack),

    # url:"/attack_make",
    path('attack_make', views.attack_make),

    path('completeSystem', views.complete_system),

    # 写入了一个比较简单的ajax？对的
    path('first_table', views.first_detect),
    path('second_table', views.second_detect),
    path('third_table', views.third_detect),
    path('fourth_table', views.fourth_detect),

    path('see_anormal_data', views.see_anormal_data),

    path('cloud_system', views.cloud_system),
    path('parse_cloud_system', views.parse_cloud_system),
    path('detect_cloud_system', views.detect_cloud_system),
    path('upload_cloud_system_parse/', views.upload_cloud_system_parse),
    path('upload_cloud_system_detect/', views.upload_cloud_system_detect),

    # 此外，还要加入一些基础的动态AJAX，典型的LSTM就需要单独拉出来，降低时间复杂度？对滴
]
