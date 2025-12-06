from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("search/", views.post_search, name="post_search"),
    path("category/<slug:slug>/", views.CategoryPostListView.as_view(), name="category_detail"),
    path("tag/<slug:slug>/", views.TagPostListView.as_view(), name="tag_detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("post/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("comment/<int:pk>/approve/", views.comment_approve, name="comment_approve"),
    path("comment/<int:pk>/delete/", views.comment_delete, name="comment_delete"),
    path("dashboard/", views.AuthorDashboardView.as_view(), name="author_dashboard"),
]
