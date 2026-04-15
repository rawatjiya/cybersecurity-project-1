from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import Note
from django.db import connection

def index(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    notes = Note.objects.filter(owner=request.user)
    return render(request, "core/index.html", {"notes": notes})


##FLAW 1: A02: Cryptographic Failures vulnerability
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create(username=username, password=password) #This is insecure because it stores the password in plaintext.
        login(request, user)
        return redirect("/")

    return render(request, "core/register.html")


"""""
##FLAW 1 FIX: Use Django's built-in user creation which hashes passwords securely.
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("/")
    return render(request, "core/register.html")
"""


 ###FLAW 2: A07: Identification and Authentication Failures vulnerability
def user_login(request):
    attempts = request.session.get("login_attempts", 0)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)

            if user.password == password:
                request.session["login_attempts"] = 0
                login(request, user)
                return redirect("/")
            else:
                attempts += 1
                request.session["login_attempts"] = attempts

        except User.DoesNotExist:
            attempts += 1
            request.session["login_attempts"] = attempts
    return render(request, "core/login.html", {"attempts": attempts})

""" 
##FLAW 2 FIX: Implement account lockout after a certain number of failed attempts.
import time

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300

def user_login(request):
    attempts = request.session.get("login_attempts", 0)
    lockout_until = request.session.get("lockout_until")

    if lockout_until and time.time() < lockout_until:
        return HttpResponse("Account locked. Try again later.", status=403)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)

            if user.password == password:
                request.session["login_attempts"] = 0
                request.session.pop("lockout_until", None)
                login(request, user)
                return redirect("/")
            else:
                attempts += 1

        except User.DoesNotExist:
            attempts += 1

        request.session["login_attempts"] = attempts

        if attempts >= MAX_ATTEMPTS:
            request.session["lockout_until"] = time.time() + LOCKOUT_TIME

    return render(request, "core/login.html", {"attempts": attempts})
"""


def user_logout(request):
    logout(request)
    return redirect("/login/")


def create_note(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Note.objects.create(
            title=title,
            content=content,
            owner=request.user
        )

        return redirect("/")
    return render(request, "core/create.html")


def note_detail(request, note_id):
    if not request.user.is_authenticated:
        return redirect("/login/")
    ##FLAW 3: A01: Broken Access Control vulnerability
    note = Note.objects.get(id=note_id) 
    ##FLAW 3 FIX: Add control check 
    #if note.owner != request.user:
        #return HttpResponse("Unauthorized", status=403)
    return render(request, "core/detail.html", {"note": note})

def search(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    query = request.GET.get("q")

    notes = []

    if query:
        
        cursor = connection.cursor()
        ##FLAW 4: A03: SQL Injection vulnerability
        cursor.execute(f"SELECT * FROM core_note WHERE title LIKE '%{query}%' AND owner_id = {request.user.id}")
        ##FLAW 4 FIX:
        #cursor.execute("SELECT * FROM core_note WHERE title LIKE %s AND owner_id = %s", [f"%{query}%", request.user.id])
        
        rows = cursor.fetchall()

        for row in rows:
            note = Note(id=row[0], title=row[1], content=row[2], owner_id=row[3])
            notes.append(note)


    return render(request, "core/search.html", {"notes": notes})
