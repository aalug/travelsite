"""Views for the forum app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView
from django.contrib import messages

from accounts.models import UserProfile
from forum.models import Post, PostCategory, Comment, Author, Reply
from forum.utils import get_post_categories_with_parents_and_children, get_posts_data, update_hits


class MainForumPageView(TemplateView):
    """Main forum page view."""
    template_name = 'forum/forum_main_page.html'

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
        context['posts_data'] = get_posts_data(number_of_posts=3)
        context['categories'] = get_post_categories_with_parents_and_children()
        context['categories_w_last_posts'] = self.get_categories_with_last_posts()
        return context


class PostsByCategoryView(ListView):
    """View for posts by category page."""
    template_name = 'forum/posts_by_category.html'
    context_object_name = 'posts_data'
    paginate_by = 10

    def get_queryset(self):
        """Gets queryset - by default sorted by -created_at,
           if changed and sent in request.GET - sorted accordingly."""
        if self.request.GET:
            sorting_dict = {
                'popularity': '-hit_count_generic__hits',
                'date-desc': '-created_at',
                'date-asc': 'created_at',
            }
            order_by = sorting_dict[self.request.GET.get('sort-by')]
            posts_data = get_posts_data(category_slug=self.kwargs.get('slug'), order_by=order_by)
        else:
            posts_data = get_posts_data(category_slug=self.kwargs.get('slug'))
        return posts_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['categories'] = get_post_categories_with_parents_and_children()
        context['current_category'] = get_object_or_404(PostCategory, slug=self.kwargs.get('slug'))
        return context


class PostDetailView(TemplateView):
    """View for post details.
       Displays Post, comments (paginated), and replies to each comment."""
    template_name = 'forum/post_details.html'

    def get_comments_data(self):
        """Gets all data needed for comment section - comments, UserProfiles of authors,
           and replies (also with UserProfiles of authors)."""
        comments = get_object_or_404(Post, slug=self.kwargs.get('slug')).comments.all()
        comments_authors_and_replies = []
        for comment in comments:
            user_profile = get_object_or_404(UserProfile, user=comment.author.user)
            # Get all replies and UserProfiles of authors
            replies = []
            for reply in comment.replies.all():
                profile = get_object_or_404(UserProfile, user=reply.author.user)
                replies.append((reply, profile))

            comments_authors_and_replies.append((comment, user_profile, replies))
        return comments_authors_and_replies

    def paginated_comments_data(self):
        """Paginate data from self.get_comments_data()."""
        data = self.get_comments_data()
        paginator = Paginator(data, 10)
        page = self.request.GET.get('page')
        data_on_page = paginator.get_page(page)
        return data_on_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        user_profile = get_object_or_404(UserProfile, user=post.author.user)
        update_hits(self.request, post)
        context['post'] = post
        context['author_user_profile'] = user_profile
        context['comments_authors_and_replies'] = self.paginated_comments_data()
        return context


class AddCommentView(LoginRequiredMixin, View):
    """Gets the comment content from request.POST and creates Comment.
       After, redirects back to the page."""

    def post(self, request):
        content = request.POST.get('comment-content')
        post_id = request.POST.get('post-id')
        author = Author.objects.get_or_create(user=request.user)[0]

        comment = Comment.objects.create(
            author=author,
            content=content
        )
        post = get_object_or_404(Post, pk=post_id)
        post.comments.add(comment)
        post.save()
        messages.success(request, 'Comment was sent successfully.')
        return redirect('post-detail', slug=post.slug)


class AddReplyView(LoginRequiredMixin, View):
    """Gets the reply content from request.POST and creates Reply.
       After, redirects back to the page."""

    def post(self, request):
        comment_id = request.POST.get('comment-id')
        post_slug = request.POST.get('post-slug')
        content = request.POST.get('reply')
        author = Author.objects.get_or_create(user=request.user)[0]

        reply = Reply.objects.create(
            author=author,
            content=content
        )
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.replies.add(reply)
        comment.save()
        messages.success(request, 'Reply was sent successfully.')
        return redirect('post-detail', slug=post_slug)
