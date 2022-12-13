from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.shortcuts import reverse
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from tinymce.models import HTMLField
from taggit.managers import TaggableManager
from hitcount.models import HitCount
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """Author table. It extends User model by slug - to be able to display
       posts by author, and points - as kind of reputation score."""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)

    @property
    def num_posts(self):
        return Post.objects.filter(author=self).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.user))
        super(Author, self).save(*args, **kwargs)


class PostCategory(MPTTModel):
    """Category table implemented with MPTT."""
    name = models.CharField(max_length=100, unique=True,
                            verbose_name=_('category name'),
                            help_text=_('format: required, max=100'))

    slug = models.SlugField(max_length=150, null=True, unique=True,
                            verbose_name=_('category safe URL'),
                            help_text=_('format: letters, numbers, underscores or hyphens'))
    description = models.TextField(default='description', null=True)
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            related_name='children',
                            null=True,
                            blank=True,
                            verbose_name='parent of category',
                            help_text=_('format: not required'))
    cover_photo = models.ImageField(null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('post category')
        verbose_name_plural = _('post categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(PostCategory, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('posts-by-category', kwargs={
            'slug': self.slug
        })

    @property
    def num_posts(self):
        return Post.objects.filter(categories=self).count()

    @property
    def last_post(self):
        return Post.objects.filter(categories=self).latest('created_at')


class Reply(models.Model):
    """Reply table."""
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:100]

    class Meta:
        verbose_name_plural = _('replies')


class Comment(models.Model):
    """Comment table."""
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    replies = models.ManyToManyField(Reply, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:100]


class Post(models.Model):
    """Post table."""
    title = models.CharField(max_length=400, unique=True)
    slug = models.SlugField(max_length=430, unique=True, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = HTMLField()
    categories = models.ManyToManyField(PostCategory, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    tags = TaggableManager()
    comments = models.ManyToManyField(Comment, blank=True)
    closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse('post-detail', kwargs={
            'slug': self.slug
        })

    @property
    def num_comments(self):
        return self.comments.count()
