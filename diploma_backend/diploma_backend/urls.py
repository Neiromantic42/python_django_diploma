"""
URL configuration for diploma_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent / 'diploma-frontend'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')), # подключает все фронтенд-шаблоны
    path('api/', include('products.urls')), # подключаем все пути приложения products
    path('api/', include('users.urls')), # подключаем все пути приложения users
    path('api/', include('basket.urls')), # подключаем все пути прилодения basket
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)