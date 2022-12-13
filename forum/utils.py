"""Utils for the forum app."""
from django.shortcuts import get_object_or_404

from accounts.models import UserProfile
from forum.models import PostCategory, Post


def get_post_categories_with_parents_and_children():
    """Returns categories with distinction, which categories are parents
       and which ones are children."""
    categories = PostCategory.objects.filter(is_active=True)
    categories_dict = {}

    for category in categories:
        if not category.parent:
            categories_dict.update({
                category: []
            })
        else:
            categories_dict[category.parent].append(category)

    return categories_dict


def get_posts_data(number_of_posts: int = None, category_slug: str = None) -> list[tuple]:
    """Returns posts with UserProfile of an author.
       If number_of_posts argument is passed, then the queryset is sliced.
       If category_slug argument is passed, then there is additional filter.
       If none of the arguments is passed, the function will return all
       approved and not closed posts with UserProfiles of authors."""

    if category_slug is not None:
        posts = Post.objects.filter(is_approved=True,
                                    closed=False,
                                    categories__slug=category_slug).order_by('-created_at')
    else:
        posts = Post.objects.filter(is_approved=True, closed=False).order_by('-created_at')

    # Number of post was passed, slice the queryset
    if number_of_posts is not None:
        posts = posts[:number_of_posts]

    posts_data = []
    for post in posts:
        user_profile = get_object_or_404(UserProfile, user=post.author.user)

        posts_data.append(
            (post, user_profile)
        )
    return posts_data
