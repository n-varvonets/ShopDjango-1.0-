"""DemoRest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include

# инклдим урлы в олдном основном месте с разных

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/base-auth/', include('rest_framework.urls')),  # 1)подключаем рестовскую аутентификацию + сериалайз
    # смотри http://i.imgur.com/Ildva33.png  http://i.imgur.com/ZQLkD1y.png
    # 2)id сессия выдается при аутентификации и к нему прикрепляется пользователь. заходим под админом(admin 1234) и...
    # создаем инстанс юезра и сессию(у ссесии есть куки, где берем все нужные данные) http://i.imgur.com/92nE6bl.png с HiddenField  удачно постим новую запись
    # 3)Дальше создадим пермисион для редактирования записи только пользователем создателдем http://i.imgur.com/TsaSpZF.png

    path('api/v1/cars/', include('cars.urls')),  # есть стиль описания апи, вот он такой как написал
    path('api/v1/auth/', include('djoser.urls')), #  и если перейдем по урл, он нам выведит что он может()
    path('api/v1/auth_token/', include('djoser.urls.authtoken')),  #  напишем так же ауф с помощью токена + в setiing.py
    #  нужно у реста создать(взять билдиновскую) модель токенов или сделать свою(но не сейчас) http://i.imgur.com/a9wH4Af.png


]

"""для создания полтзователя используем библиотеку  Djoser (https://www.django-rest-framework.org/api-guide/authentication/#djoser)
 - она прекрасмно работает на базовых уровнях. Если же понадобится двухфаторная аутентификация, собственная регистрация,
восстановления пароля, то будем писать её свою(не забудь указать в аппликейшенах ее setting.py):
"""