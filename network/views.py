from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .forms import PostForm
from .models import Post, User, Follow


def index(request):
    posts = Post.objects.all()
    form = PostForm()
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        form = PostForm(request.POST)
        if form.is_valid():
            # doesn't save right away in database
            post = form.save(commit=False)
            post.author = user
            post.save()
            return HttpResponseRedirect(reverse("index"))
    context = {
        'posts': posts,
        'form': form
    }
    return render(request, "network/index.html", context)


def profile(request, username):
    if request.method == 'GET':
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(
            author=profileuser).order_by('id').reverse()
        follower = Follow.objects.filter(target=profileuser)
        following = Follow.objects.filter(follow=profileuser)
        if request.user.is_anonymous:
            return redirect('login')
        else:
            following_each_other = Follow.objects.filter(
                follow=currentuser, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts,
                'posts_count': posts.count(),
                'profileuser': profileuser,
                'follower': follower,
                'totalfollower': totalfollower,
                'following': following,
                'totalfollowing': totalfollowing,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)

    else:
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(
            author=profileuser).order_by('id').reverse()
        following_each_other = Follow.objects.filter(
            follow=request.user, target=profileuser)

        if not following_each_other:
            follow = Follow.objects.create(
                target=profileuser, follow=currentuser)
            follow.save()
            follower = Follow.objects.filter(target=profileuser)
            following = Follow.objects.filter(follow=profileuser)
            following_each_other = Follow.objects.filter(
                follow=request.user, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'follower': follower,
                'following': following,
                'totalfollowing': totalfollowing,
                'totalfollower': totalfollower,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)

        else:
            following_each_other.delete()
            follower = Follow.objects.filter(target=profileuser)
            following = Follow.objects.filter(follow=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'follower': follower,
                'following': following,
                'totalfollowing': totalfollowing,
                'totalfollower': totalfollower,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
