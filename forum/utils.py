"""Utils for forum app."""

from forum.models import PostCategory
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin


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
