import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, User, Follow, Like


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
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'form': form,
        'paginator': paginator,
        'page_obj': page_obj
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

            paginator = Paginator(posts, 3)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'posts': posts,
                'posts_count': posts.count(),
                'profileuser': profileuser,
                'follower': follower,
                'totalfollower': totalfollower,
                'following': following,
                'totalfollowing': totalfollowing,
                'followingEachOther': following_each_other,
                'paginator': paginator,
                'page_obj': page_obj
            }

            return render(request, "network/profile.html", context)

    else:
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(
            author=profileuser).order_by('id').reverse()
        following_each_other = Follow.objects.filter(
            follow=request.user, target=profileuser)
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

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
                'followingEachOther': following_each_other,
                'paginator': paginator,
                'page_obj': page_obj
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
                'followingEachOther': following_each_other,
                'paginator': paginator,
                'page_obj': page_obj
            }

            return render(request, "network/profile.html", context)


def following(request):
    posts = Post.objects.all()
    currentuser = request.user
    followingposts = []
    for post in posts:
        if post.author != currentuser:
            followingposts.append(post)
    paginator = Paginator(followingposts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'followingposts': followingposts,
        'paginator': paginator,
        'page_obj': page_obj
    }

    return render(request, "network/following.html", context)


@csrf_exempt
@login_required
def edit(request, post_id):
    # Query for requested post
    post = Post.objects.get(author=request.user, id=post_id)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return HttpResponse(status=204)


@csrf_exempt
def like(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "GET":
        return JsonResponse(post.serialize())

    if request.method == "PUT":
        data = json.loads(request.body)
        print(data.get("like"))
        if data.get("like"):
            Like.objects.create(user=request.user, post=post)
            post.likes = Like.objects.filter(post=post).count()
        else:  # unlike
            Like.objects.filter(user=request.user, post=post).delete()
            post.likes = Like.objects.filter(post=post).count()
        post.save()
        return HttpResponse(status=204)


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
