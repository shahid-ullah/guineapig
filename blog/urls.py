from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    # path('', views.PostListView.as_view(), name='home'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
        views.post_detail,
        name='post_detail'),
    path('csv/',views.Some_view, name='csv'),
    path('highlight/<int:pk>/',views.HighlightView.as_view(), name='hightlight'),
    path('pdf/',views.pdf_view, name='pdf'),
    path('new/', views.NewPostView.as_view(), name='post_new'),
    path('<int:pk>/update/', views.PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('today/', views.PostTodayArchiveView.as_view(),name="today_post"),
    path('archive/', views.PostArchiveIndexView.as_view(),name="today_archive"),
    path('<int:year>/', views.PostYearArchiveView.as_view(),name="post_year_archive"),
    path('<int:year>/<int:month>/', views.PostMonthArchiveView.as_view(month_format="%m"),name="archive_month_numeric"),
    path('<int:year>/<str:month>/', views.PostMonthArchiveView.as_view(),name="archive_month"),

    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('about/', views.about_me, name='about_me'),
    path('books/', views.ImageView.as_view(), name='books'),
    path('upload/', views.ImageUploadView.as_view(), name='image_upload'),
    path('', views.post_list, name='home'),

]
