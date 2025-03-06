from django.shortcuts import render

def index(request):
    return render(request, 'tracker/index.html')

def staff_login(request):
    return render(request, 'tracker/staff_login.html')

def staff_signup(request):
    return render(request, 'tracker/staff_signup.html')
def staff_profile(request):
    return render(request, 'tracker/staff_profile.html')
def staff_info(request):
    return render(request, 'tracker/staff_info.html')
def user_main(request):
    return render(request, 'tracker/user_main.html')
def user_map(request):
    return render(request, 'tracker/user_map.html')