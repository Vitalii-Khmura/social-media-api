from django.contrib.auth import get_user_model
from rest_framework import serializers

from social.models import User, Profile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "gender",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class MyProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=False)
    username = serializers.CharField(
        source="user.username",
        read_only=False
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=False
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=False
    )
    gender = serializers.ChoiceField(
        source="user.gender",
        read_only=False,
        choices=User.GenderChoices.choices
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "email",
            "profile_image",
            "first_name",
            "last_name",
            "hobby",
            "gender"
        )

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return Profile().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            fields_to_update = ["username", "first_name", "last_name", "email", "gender"]
            for field in fields_to_update:
                setattr(instance.user, field, user_data.get(field, getattr(instance.user, field)))

        instance.user.save()

        instance.hobby = validated_data.get("hobby", instance.hobby)
        instance.profile_image = validated_data.get("profile_image", instance.profile_image)
        instance.save()

        return instance


class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=False
    )

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "full_name"
        )

    @staticmethod
    def get_full_name(obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    STATUS_CHOICES = (
        ('follow', 'Follow'),
        ('unfollow', 'Unfollow'),
    )
    following = serializers.SerializerMethodField()
    follow = serializers.ChoiceField(choices=STATUS_CHOICES)
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True
    )
    gender = serializers.ChoiceField(
        source="user.gender",
        read_only=True,
        choices=User.GenderChoices.choices
    )

    class Meta:
        model = Profile
        fields = (
            "username",
            "profile_image",
            "first_name",
            "last_name",
            "hobby",
            "gender",
            "following"
        )
