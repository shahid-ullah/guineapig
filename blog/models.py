# blog/models.py

import mistune
from django.db.models import Count
from django import template

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        print("code")
        print(code)
        print()
        print("language")
        print(lang)
        print()
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)


def markdown_format(post):
    renderer = HighlightRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(post)

from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

from taggit.managers import TaggableManager
# from markdownx.models import MarkdownxField
from bs4 import BeautifulSoup
from pygments import highlight, formatters, lexers


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,
                     self).get_queryset().filter(status='published')


class ImageStore(models.Model):
    title = models.TextField()
    cover = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Images"


class Post(models.Model):
    tags = TaggableManager()
    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # Our custom manager.
    CONTENT_LANGUAGE_CHOICES = (
        ('html', 'HTML',),
        ('mark', 'Markdown'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    language = models.CharField(max_length=20,
                                choices=CONTENT_LANGUAGE_CHOICES,
                                default='html',
                                help_text="Select Content Language")
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish', blank=True, null=True)
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()
    body_content = models.TextField(blank=True, null=True, editable=False)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='draft')

    class Meta:
        ordering = ('-publish',)

    def save(self, *args, **kwargs):
        print("Save method called")
        if not self.id:
            self.slug = slugify(self.title)
        self.body_content = markdown_format(self.body)

        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        published_localtime = timezone.localtime(self.publish)
        # return reverse('blog:post_detail',
        #                args=[self.publish.year,
        #                      self.publish.month,
        #                      self.publish.day,
        #                      self.slug])
        return reverse('blog:post_detail',
                       args=[published_localtime.year,
                             published_localtime.strftime('%m'),
                             published_localtime.strftime('%d'),
                             self.slug])


class HighlightCode(models.Model):
    body = models.TextField()
    body_highlighted = models.TextField(editable=False, blank=True)

    def save(self, force_insert=False, force_update=False):
        self.body_highlighted = self.highlight_code(self.body)
        super(HighlightCode, self).save(force_insert, force_update)

    def highlight_code(self, html):
        #  create BeautifulSoup object using self.body content

        soup = BeautifulSoup(html)
        #  collect all pre block content
        preblocks = soup.findAll('pre')
        for pre in preblocks:
            # all changes are occured inline
            if pre.has_key('class'):
                try:
                    # list to string conversion
                    code = ''.join([str(item) for item in pre.contents])
                    code = self.unescape_html(code)
                    lexer = lexers.get_lexer_by_name(pre['class'][0])
                    formatter = formatters.HtmlFormatter()
                    code_hl = highlight(code, lexer, formatter)
                    pre.replaceWith(BeautifulSoup(code_hl))
                except:
                    pass
        #  retuned changed soup content
        return str(soup)

    def unescape_html(self, html):
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&amp;', '&')
        return html


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)
