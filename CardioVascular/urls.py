"""CardioVascular URL Configuration

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
from django.urls import path
from CardioVascular import views as view
from users import views as usr
from admins import  views as admns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', view.index, name='index'),
    path('logout/', view.logout, name='logout'),
    path('UserRegister/', view.UserRegister, name='UserRegister'),

    # user Based users
    path('UserRegisterAction/', usr.UserRegisterAction, name='UserRegisterAction'),
    path('UserLogin/', usr.UserLogin, name='UserLogin'),
    path('UserLoginCheck', usr.UserLoginCheck, name='UserLoginCheck'),
    path('UploadCSVToDataBase/',usr.UploadCSVToDataBase,name='UploadCSVToDataBase'),
    path('BrowseCSV/',usr.BrowseCSV,name='BrowseCSV'),
    path('DataPreparations/',usr.DataPreparations,name='DataPreparations'),
    path('UserMachineLearning/',usr.UserMachineLearning,name='UserMachineLearning'),
    path('UserDataView/',usr.UserDataView,name='UserDataView'),
    path('UserAddData/',usr.UserAddData,name='UserAddData'),


    ##Admin urls
    path('AdminLoginCheck/',admns.AdminLoginCheck,name='AdminLoginCheck'),
    path('AdminLogin/',admns.AdminLogin,name='AdminLogin'),
    path('RegisterUsersView/',admns.RegisterUsersView,name='RegisterUsersView'),
    path('ActivaUsers/',admns.ActivaUsers,name='ActivaUsers'),
    path('AdminDataView/',admns.AdminDataView,name='AdminDataView'),
    path('AdminMachineLearning/',admns.AdminMachineLearning,name='AdminMachineLearning'),
]
