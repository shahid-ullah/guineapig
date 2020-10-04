import csv
import io
# import os

from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from taggit.models import Tag
from reportlab.pdfgen import canvas
from django.views.generic.dates import (
            TodayArchiveView,
            ArchiveIndexView,
            YearArchiveView,
            MonthArchiveView,
            )

from .forms import CommentForm, EmailPostForm, ImageUploadForm
from .models import Post, HighlightCode, ImageStore


class ImageView(ListView):
    model = ImageStore
    template_name = 'image_view.html'


class ImageUploadView(CreateView):
    model = ImageStore
    form_class = ImageUploadForm
    template_name = 'image_upload.html'
    success_url = reverse_lazy('blog:books')


def post_list(request, tag_slug=None):
    posts = Post.published.all()
    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    return render(request, 'blog/home.html', {'posts': posts, 'tag': tag})

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     template_name = 'blog/home.html'


class NewPostView(CreateView):
    model = Post
    template_name = 'blog/post_new.html'
    fields = ['tags', 'language', 'title', 'author', 'body', 'status', ]


class PostUpdate(UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    fields = ['tags', 'title', 'slug', 'body', 'status', ]


class PostDelete(DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    success_url = reverse_lazy('blog:home')


# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/post_detail.html'


def post_detail(request, year, month, day, post):

    # post = get_object_or_404(Post, slug=post,
    #                         status='published',
    #                         publish__year=year,
    #                         publish__month=month,
    #                         publish__day=day)
    post = get_object_or_404(
                            Post, slug=post,
                            status='published',
                            )
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
                                        tags__in=post_tags_ids
                                        ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by(
                                        '-same_tags', '-publish')[:4]

    return render(
                request,
                'blog/post_detail.html',
                {
                    'post': post,
                    'new_comment': new_comment,
                    'comment_form': comment_form,
                    'comments': comments,
                    'similar_posts': similar_posts
                }
                )


def post_share(request, post_id):

    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) recommends you reading "\
                    {}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments {}'.format(
                                                        post.title,
                                                        post_url,
                                                        cd['name'],
                                                        cd['comments']
                                                                    )
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(
                request,
                'blog/share.html',
                {'post': post, 'form': form, 'sent': sent})


def some_view(request):

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(
                ['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"]
                  )

    return response


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def some_streaming_csv_view(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
                                    (writer.writerow(row) for row in rows),
                                    content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response


def Some_view(request):

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    # The data is hard-coded here, but you could load it from a database or
    # some other source.
    csv_data = (
        ('First row', 'Foo', 'Bar', 'Baz'),
        ('Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"),
    )
    t = loader.get_template('my_template_name.txt')
    c = {'data': csv_data}
    response.write(t.render(c))
    return response


def pdf_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    body = Post.published.get(id=1).body
    body = str(body)
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, body)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, filename='hello.pdf')


class PostTodayArchiveView(TodayArchiveView):
    queryset = Post.published.all()
    date_field = "updated"
    allow_future = True


class PostArchiveIndexView(ArchiveIndexView):
    queryset = Post.published.all()
    date_field = "updated"
    allow_future = True


class PostYearArchiveView(YearArchiveView):
    queryset = Post.published.all()
    date_field = "publish"
    make_object_list = True
    allow_future = True


class PostMonthArchiveView(MonthArchiveView):
    queryset = Post.published.all()
    date_field = "publish"
    allow_future = True


class HighlightView(DetailView):
    model = HighlightCode
    template_name = 'blog/highlight_code.html'


def about_me(request):

    return render(request, 'blog/about.html')
