# tasks/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwnerOrReadOnly


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task API with filtering and ordering:
      - ?q=<text>           -> title__icontains (search)
      - ?status=<value>     -> todo|inprogress|done, also 'pending' and 'completed'
      - ?favorite=1         -> is_favorite=True
      - ?ordering=<value>   -> ordering field/alias:
            allowed aliases: newest, oldest, title_asc, title_desc
            allowed direct fields: created_at, -created_at, title, -title
    """
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user is None or not user.is_authenticated:
            return Task.objects.none()

        qs = Task.objects.filter(owner=user)

        # text search (title)
        q = self.request.GET.get('q') or self.request.GET.get('search')
        if q:
            q = q.strip()
            if q:
                qs = qs.filter(title__icontains=q)

        # status filter
        status_param = (self.request.GET.get('status') or '').strip().lower()
        if status_param:
            if status_param in ('todo', 'inprogress', 'done'):
                qs = qs.filter(status=status_param)
            elif status_param == 'pending':
                qs = qs.exclude(status='done')
            elif status_param == 'completed':
                qs = qs.filter(status='done')

        # favorite filter
        fav = self.request.GET.get('favorite')
        if fav is not None:
            fav_val = str(fav).lower() in ('1', 'true', 'yes')
            if fav_val:
                qs = qs.filter(is_favorite=True)
            else:
                qs = qs.filter(is_favorite=False)

        # ordering: map friendly aliases to fields, but allow direct safe fields too
        ordering = (self.request.GET.get('ordering') or '').strip()
        if ordering:
            mapping = {
                'newest': '-created_at',
                'oldest': 'created_at',
                'title_asc': 'title',
                'title_desc': '-title',
                # keep keys for backward compatibility:
                'created_at': 'created_at',
                '-created_at': '-created_at',
                'title': 'title',
                '-title': '-title',
            }
            order_field = mapping.get(ordering, None)
            # If not in mapping, only allow safe direct fields (prevent SQL injection)
            if order_field is None:
                if ordering in ('created_at', '-created_at', 'title', '-title'):
                    order_field = ordering
            if order_field:
                qs = qs.order_by(order_field)
        else:
            # default ordering (most recent first)
            qs = qs.order_by('-created_at')

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle-favorite')
    def toggle_favorite(self, request, pk=None):
        task = self.get_object()
        task.is_favorite = not task.is_favorite
        task.save()
        return Response({'id': task.id, 'is_favorite': task.is_favorite}, status=status.HTTP_200_OK)


# server-rendered tasks home page view (root)
@login_required
def tasks_index(request):
    return render(request, 'tasks_index.html')
