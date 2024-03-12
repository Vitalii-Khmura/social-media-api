from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from social.views import UserViewSet, ProfileSearchViewSet, ProfileManegeAPIView

router = routers.DefaultRouter()

router.register("register", UserViewSet)
router.register("search", ProfileSearchViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("profile/", ProfileManegeAPIView.as_view(), name="profile"),
    path('search/<int:pk>/follow/', ProfileSearchViewSet.as_view({'post': 'follow'}),name='profile-follow'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "social"
