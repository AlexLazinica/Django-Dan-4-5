from rest_framework import serializers
from tasks.models import Task, TaskList
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
        ]


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = ["id", "name", "user"]
        read_only_fields = ["user"]


class TaskSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "is_completed",
            "created_at",
            "updated_at",
            "user_details",
            "task_list",
        ]
        read_only_fields = ["id", "crated_at", "updated_at"]

    def validate_title(self, value):
        if len(value) < 7:
            raise serializers.ValidationError("Title length must be at least 7 chars!")
        return value

    def validate(self, data):
        if (
            data.get("title")
            and data.get("description")
            and data["title"] == data["description"]
        ):
            raise serializers.ValidationError(
                "Title and description can not be the same!"
            )
        return data