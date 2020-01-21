from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createUser', views.createUser, name='createUser'),
    path('deleteUser', views.deleteUser, name='deleteUser'),
    path('login', views.loginPage, name='loginPage'),
    path('logout', views.logoutPage, name='logoutPage'),
    path('protected', views.protected, name='protected'),
    path('uploadPicture', views.uploadPicture, name='uploadPicture'),
    path('getPictureList', views.getPictureList, name='getPictureList'),
    path('getPicture', views.getPicture, name='getPicture'),
    path('getPictureProcessed', views.getPictureProcessed, name='getPictureProcssed'),
    path('testProcessAllNewTasks', views.testHelperProcessAllNewTasks, name='testProcessAllNewTasks'),
]
