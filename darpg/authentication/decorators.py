from django.shortcuts import redirect
from functools import wraps

def redirect_authenticated_user(view, redirect_to='auth:home'):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(redirect_to)
        else:
            return view(request, *args, **kwargs)
    return wrapper

def only_authenticated_user(view, redirect_to='auth:signin'):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect(redirect_to)
        else:
            return view(request, *args, **kwargs)
    return wrapper

def reviewer_required(view_func, redirect_to='auth:signin'):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_reviewer():
            return view_func(request, *args, **kwargs)
        else:
            return redirect(redirect_to)
    return wrapper