from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserRegisterForm


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            reader_group, _ = Group.objects.get_or_create(name="Reader")
            user.groups.add(reader_group)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("blog:post_list")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("blog:post_list")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})
