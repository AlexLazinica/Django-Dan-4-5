from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from tasks.models import Task, TaskList
from django.http import Http404

from tasks.permissions import IsTaskOwnerOrAdmin
from .serializers import TaskListSerializer, TaskSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView


class TaskListView(APIView):
    def get(self, request):
        if request.user.is_superuser:
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(user=request.user)
        tasks_serialized = TaskSerializer(queryset, many=True)
        return Response(tasks_serialized.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAdmin]

    def get_object(self, pk):
        try:
            task_object = Task.objects.get(id=pk)
            self.check_object_permissions(self.request, task_object)
            return task_object
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if request.user.has_perm("tasks.delete_task"):
            task = self.get_object(pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "You do not have permission to delete tasks!"},
                status=status.HTTP_403_FORBIDDEN,
            )

    def put(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListListView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = TaskListSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TaskList.objects.all()
        return TaskList.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskListDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TaskList.objects.all()
        return TaskList.objects.filter(user=self.request.user)