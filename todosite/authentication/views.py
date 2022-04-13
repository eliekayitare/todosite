
from multiprocessing import context
from tkinter import N
from django.shortcuts import redirect, render
#authentication
from .models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
#validating email
from validate_email import validate_email

#logout required
from helpers.decorators import auth_user_should_not_access
from .models import User

#activating email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str,force_text,DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage

import threading

from django.conf import settings
# Create your views here.



#allowing sending email functionality to be fast using threading

class EmailThread(threading.Thread):

    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()





def  send_activation_email(user,request):
    current_site = get_current_site(request)
    email_subject = 'Hey, Activate your account'
    email_body = render_to_string('authentication/activate_email.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':generate_token.make_token(user)
    })

    email=EmailMessage(subject=email_subject,body=email_body,from_email=settings.DEFAULT_FROM_EMAIL,to=[user.email])

    EmailThread(email).start()

@auth_user_should_not_access
def register(request):
    if request.method=="POST":
        context={"has_error":False,"data":request.POST}
        first_name=request.POST['fname']
        last_name=request.POST['lname']
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password!=confirm_password:
            messages.add_message(request,messages.ERROR,"Passwords must be same")
        if len(password)<6:
            messages.add_message(request,messages.ERROR,"Passwords length should be >=6 ")
            context['has_error']=True
        if not(validate_email(email)):

            messages.add_message(request,messages.ERROR,"Please enter a valid email address")
            context['has_error']=True
        if not username:
            messages.add_message(request,messages.ERROR,"Username is required")
            context['has_error']=True
        if User.objects.filter(username=username).exists():
            messages.add_message(request,messages.ERROR,"Username already taken")
            context['has_error']=True
        if User.objects.filter(email=email).exists():
            messages.add_message(request,messages.ERROR,"Email already taken")
            context['has_error']=True

        if context['has_error']:
            return render(request,'authentication/register.html',context)


        user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email)
        user.set_password(password)
        send_activation_email(user,request)
        user.save()
        messages.add_message(request,messages.SUCCESS,"Account created successfully,Verify your account before login")
        return redirect('login')

    return render(request,'authentication/register.html')


@auth_user_should_not_access
def user_login(request):
    if request.method=="POST":
        context={"data":request.POST}
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)

        if not user.is_email_verified:
            messages.add_message(request,messages.ERROR,"Email is not verified,Please check your inbox")

            return render(request,'authentication/login.html',context)
            


        if not user:
            messages.add_message(request,messages.ERROR,"Invalid credentials")
            return render(request,'authentication/login.html',context)

    
        login(request,user)
        messages.add_message(request,messages.SUCCESS,f'welcome  {user.username}')
        return redirect('home')
        
    return render(request,'authentication/login.html')


def logout_user(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS,'Logout successfully')

    return redirect('login')
    
def activate_user(request,uidb64,token):

    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    
    except Exception as e:
        user=None

    #check if a token has not been used
    if user and generate_token.check_token(user,token):
        user.is_email_verified = True
        user.save()
        messages.add_message(request,messages.SUCCESS,'Email verified, you can now login')
        return redirect('login')
    return render(request,'authentication/activation_failed.html',{"user":user})



    
  
