from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Room, Topic, Message, User
from .forms import RoomForm, UpdateUserForm, RegisterForm


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "Email doesn't exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password doesn't exist")
        
    context={}
    return render(request, "base/login.html", context)


def logout_user(request):
    logout(request)
    return redirect("home")


def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")
    context = {"form": form}
    return render(request, "base/signup.html", context)


def home(request):
    query = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms: list = Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    topics: list = Topic.objects.all()[:5]
    room_count: int = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    context: dict = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    if request.method == "POST":
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants
    }
    return render(request, "base/room.html", context)


def user_profile(request, pk):
    try:
        user = User.objects.get(id=pk)
    except:
        return HttpResponse("Not found")
    
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def create_room(request):
    form = RoomForm
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, _ = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get("name"),
            description = request.POST.get("description"),
        )
        return redirect("home")

    context={"form": form, "topics": topics}
    return render(request, "base/create-room.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Not allowed")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")
        
    context = {"form": form, "topics": topics, "room": room}

    return render(request, "base/create-room.html", context)


@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Not allowed")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"item": room.name})


@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Not allowed")
    
    if request.method == "POST":
        message.delete()
        return redirect("room", pk=message.room.id)
    
    context = {"item": message.body}
    
    return render(request, "base/delete.html", context)
    

@login_required(login_url="login")
def update_user(request):
    user = request.user
    form = UpdateUserForm(instance=user)

    if request.method == "POST":
        update_form = UpdateUserForm(request.POST, request.FILES, instance=user)
        if update_form.is_valid():
            update_form.save()
            return redirect("user-profile", pk=user.id)

    context = {"form": form}
    return render(request, "base/update-user.html", context)


def topics(request):
    query = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=query)

    context = {
        "topics": topics
    }

    return render(request, "base/topics.html", context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
