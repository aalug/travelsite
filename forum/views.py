from django.views.generic import DetailView, ListView

from forum.models import Post


class MainForumPageView(ListView):
    """Main forum page view."""
    template_name = 'forum/forum_main_page.html'
    queryset = Post.objects.filter(is_approved=True, closed=False).order_by('-created_at')[:6]
    context_object_name = 'posts'


class PostsByCategoryView(ListView):
    pass


class PostDetailView(DetailView):
    pass
