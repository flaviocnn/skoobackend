from django.conf.urls import url
from rest_framework import routers
from .views import (    BookViewSet,
                        DealViewSet,
                        UserView,
                        BookDetail,
                        ObtainAuthToken
                    )
from rest_framework.authtoken import views

router = routers.DefaultRouter()

router.register(r'books',BookViewSet, base_name = 'libri')
router.register(r'deals',DealViewSet)
router.register(r'users',UserView, base_name = 'utenti')

urlpatterns = [
    #url(r'^login/$',views.obtain_auth_token, name='get_auth_token'),
    url(r'^login/$',ObtainAuthToken.as_view(),),
]

urlpatterns += router.urls
