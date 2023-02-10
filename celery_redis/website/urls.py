from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView
from .views import Restore_Database,Add_S3
router = DefaultRouter()
router.register('newsapi',views.News_Data,basename='newsapi')
router.register('register',views.RegisterViewAPI,basename='RegisterAPI')
router.register('optimization',views.Cpu_optimization,basename='Optimization')
# router.register('restore',views.Restore_Database,basename='Restore')


urlpatterns = [
    path('',include(router.urls)),    
    path('verify/<token>/<pk>/',views.verify,name='verify'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('restore_database/', Restore_Database.as_view(), name='restore_database'),
    path('add-s3/', Add_S3.as_view(), name='add-s3'),

]
 