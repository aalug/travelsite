from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView

from accounts.models import UserProfile
from forum.models import Post, PostCategory, Author
from forum.utils import get_post_categories_with_parents_and_children


class MainForumPageView(TemplateView):
    """Main forum page view."""
    template_name = 'forum/forum_main_page.html'

    @staticmethod
    def get_posts_data():
        """Returns 3 newest posts with UserProfile of an author."""
        posts = Post.objects.filter(is_approved=True, closed=False).order_by('-created_at')[:3]
        posts_data = []
        for post in posts:
            user_profile = get_object_or_404(UserProfile, user=post.author.user)

            posts_data.append(
                (post, user_profile)
            )
        return posts_data

    @staticmethod
    def get_categories_with_last_posts():
        """Returns all categories, last post of this category,
           and UserProfile of an author. """
        all_categories = PostCategory.objects.filter(is_active=True)
        data = []
        for category in all_categories:
            post = category.last_post
            user_profile = get_object_or_404(UserProfile, user=post.author.user)
            data.append(
                (category, post, user_profile)
            )
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_data'] = self.get_posts_data()
        context['categories'] = get_post_categories_with_parents_and_children()
        context['categories_w_last_posts'] = self.get_categories_with_last_posts()
        return context


class PostsByCategoryView(ListView):
    """View for posts by category page."""
    template_name = 'forum/posts_by_category.html'

    def get_queryset(self):
        category = get_object_or_404(PostCategory, slug=self.kwargs.get('slug'))
        posts = Post.objects.filter(categories=category)
        return posts


class PostDetailView(TemplateView):
    """View for post details view."""
    template_name = 'forum/post_details.html'

