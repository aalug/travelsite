from django.contrib import admin

from forum.models import Author, PostCategory, Reply, Comment, Post


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class PostCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Author)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Reply)
admin.site.register(Comment)
admin.site.register(Post, PostAdmin)
