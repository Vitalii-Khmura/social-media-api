from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, generics, status

from rest_framework import viewsets, generics, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from social.models import User, Profile
from social.serializers import (
    UserSerializer,
    MyProfileSerializer,
    ProfileListSerializer,
    ProfileRetrieveSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # При створенні користувача, створюємо профіль
        Profile.objects.create(user=user)

        # Ви можете додатково налаштувати відповідь
        response_data = {
            'message': 'User created successfully with profile.'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class ProfileManegeAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = MyProfileSerializer

    def get_object(self):
        return Profile.objects.get(
            user_id=self.request.user.id
        )


class ProfileSearchViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        Profile.objects.
        prefetch_related("following").
        select_related("user")
    )
    serializer_class = ProfileListSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfileRetrieveSerializer
        return ProfileListSerializer

    def get_queryset(self):
        current_user = self.request.user
        queryset = self.queryset.exclude(pk=current_user.pk)

        user = self.request.query_params.get("user")
        username = self.request.query_params.get("username")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        if username:
            queryset = queryset.filter(
                user__username__icontains=username
            )
        if first_name:
            queryset = queryset.filter(
                user__first_name__icontains=first_name
            )
        if last_name:
            queryset = queryset.filter(
                user__last_name__icontains=last_name
            )

        return queryset

