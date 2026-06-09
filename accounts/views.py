from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegisterForm, UserForm


def register(request):
    if request.user.is_authenticated:
        return redirect("products:product_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès. Bienvenue !")
            return redirect("products:product_list")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )
