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
    path('detect/datafieldRelationship', views._detect_datafieldRalationship),
    path('construct/', views.construct),
]
