from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from taggit.models import Tag

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(status="published").select_related("author", "category").prefetch_related("tags")
def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author", "category").prefetch_related("tags", "comments__user"),
        slug=slug,
        status="published",
    )
    comments = post.comments.filter(approved=True)
    new_comment = None

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("accounts:login")
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            # default approved False; admin/author must approve
            new_comment.save()
            messages.success(request, "Comment submitted for review.")
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "comments": comments, "form": form, "new_comment": new_comment},
    )

class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        user = self.request.user
        return user.is_superuser or post.author == user

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        form.save_m2m()
        messages.success(self.request, "Post created successfully.")
        return redirect(post.get_absolute_url())

class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        post = form.save()
        messages.success(self.request, "Post updated successfully.")
        return redirect(post.get_absolute_url())

class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Post deleted successfully.")
        return super().delete(request, *args, **kwargs)
class CategoryPostListView(ListView):
    model = Post
    template_name = "blog/category_post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Post.objects.filter(
            status="published",
            category=self.category,
        ).select_related("author", "category").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context

class TagPostListView(ListView):
    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return Post.objects.filter(
            status="published",
            tags__in=[self.tag],
        ).select_related("author", "category").prefetch_related("tags").distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context

def post_search(request):
    query = request.GET.get("q", "")
    posts = Post.objects.filter(status="published")
    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog/post_search.html",
        {"page_obj": page_obj, "query": query, "posts": page_obj.object_list},
    )

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_superuser or request.user == comment.post.author:
        comment.approved = True
        comment.save()
        messages.success(request, "Comment approved.")
    else:
        messages.error(request, "You are not allowed to approve this comment.")
    return redirect(comment.post.get_absolute_url())

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_superuser or request.user == comment.post.author:
        post = comment.post
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect(post.get_absolute_url())
    messages.error(request, "You are not allowed to delete this comment.")
    return redirect(comment.post.get_absolute_url())

@method_decorator(login_required, name="dispatch")
class AuthorDashboardView(TemplateView):
    template_name = "blog/author_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superuser:
            posts = Post.objects.all()
            comments = Comment.objects.filter(approved=False)
        else:
            posts = Post.objects.filter(author=user)
            comments = Comment.objects.filter(post__author=user, approved=False)
        context["posts"] = posts
        context["pending_comments"] = comments
        return context

