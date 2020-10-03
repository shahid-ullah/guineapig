from .models import Post, Comment, HighlightCode, ImageStore
from django.contrib import admin
from django.db import models
from markdownx.admin import MarkdownxModelAdmin
from markdownx.widgets import AdminMarkdownxWidget

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # formfield_overrides = {
    #     models.TextField: {'widget': AdminMarkdownxWidget},
    # }


    list_display = ('title', 'slug', 'author', 'publish',
                    'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


# admin.site.register(Post, PostAdmin)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')



# admin.site.register(MyModel, MarkdownxModelAdmin)

admin.site.register(HighlightCode)
admin.site.register(ImageStore)
