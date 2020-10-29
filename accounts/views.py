from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def signup(request):
    if request.user.is_authenticated:

        return redirect('community:review_list')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            return redirect('community:review_list')

    else:
        form = UserCreationForm()

    context = {
        'form': form
    }

    return render(request, 'accounts/signup.html', context)



def login(request):
    if request.user.is_authenticated:
        return redirect('community:review_list')

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'community:review_list')

    else:
        form = AuthenticationForm()

    context = {
        'form': form
    }

    return render(request, 'accounts/login.html', context)


@login_required
def logout(request):
    auth_logout(request)

    return redirect('community:review_list')
