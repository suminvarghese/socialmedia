from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import CreateView,FormView,ListView, TemplateView, UpdateView
from .forms import LoginForm,UserRegistrationForm,PostForm,ProfileForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from api.models import *
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# Create your views here.

def signin_required(fn):
    def wrapper(request,*args,**kw):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session")
            return redirect("signin")
        else:
            return fn(request,*args,**kw)
    return wrapper
decs=[signin_required,never_cache]

class SignUpView(CreateView):
    template_name="register.html"
    form_class=UserRegistrationForm
    success_url=reverse_lazy("signin")
    

class SignInView(FormView):
    template_name="login.html"
    form_class=LoginForm
 
    def post(self, request,*args,**kw):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                return redirect("index")
            else:
                return render(request,self.template_name,{"form":form})

@method_decorator(decs,name="dispatch")
class IndexView(CreateView,ListView):
    template_name="index.html"
    form_class=PostForm
    success_url=reverse_lazy("index")
    model=Posts
    context_object_name="posts"

    def form_valid(self,form):
        form.instance.user=self.request.user
        messages.success(self.request,"your post added successfully")
        return super().form_valid(form)

    def get_queryset(self):
        return Posts.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["followings"] = Friends.objects.filter(follower=self.request.user)
        context["posts"] = Posts.objects.all().order_by('-created_date')
        context["notes"] = Notes.objects.all()
        return context


decs
def add_comment(request,*args,**kwargs):
    id=kwargs.get("id")
    pst=Posts.objects.get(id=id)
    cmt=request.POST.get("comment")
    Comments.objects.create(post=pst,comment=cmt,user=request.user)
    messages.success(request,"your comment posted successfully")
    return redirect("index")

@signin_required
def like_post_view(request,*args,**kw):
    id=kw.get("id")
    pst=Posts.objects.get(id=id)
    if pst.like.contains(request.user):
        pst.like.remove(request.user)
    else:
        pst.like.add(request.user)
    return redirect("index")

def signout_view(request,*args,**kw):
    logout(request)
    return redirect("signin")


class Profile(ListView):
    template_name = 'profile.html'
    model = Posts
    context_object_name="posts"

    def get_queryset(self):
        return Posts.objects.filter(user=self.request.user)

class ListPeopleView(ListView):
    template_name="list_people.html"
    model = User
    context_object_name = 'people'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["followings"] = Friends.objects.filter(follower=self.request.user)
        context["posts"] = Posts.objects.all().order_by('-created_date')
        return context
    

    def get_queryset(self):
        return User.objects.exclude(username=self.request.user)




def add_follower(request, *args, **kwargs):
    id = kwargs.get('id')
    usr = User.objects.get(id=id)
    if not Friends.objects.filter(user=usr, follower=request.user):
        Friends.objects.create(user=usr, follower=request.user)
    else:
        Friends.objects.get(user=usr, follower=request.user).delete()
    return redirect("people")


def add_notes(request, *args, **kwargs):
    id = kwargs.get('id')
    usr = User.objects.get(id=id)
    note = request.POST.get("note")
    Notes.objects.create(user=usr, note=note)
    return redirect('index')


decs
def comment_delete(request,*args,**kw):
    id=kw.get("id")
    Comments.objects.get(id=id).delete()
    return redirect("index")


decs
def post_delete(request,*args,**kw):
    id=kw.get("id")
    Posts.objects.get(id=id).delete()
    return redirect("index")



@method_decorator(decs,name="dispatch")
class EditProfile(UpdateView):
    template_name="profile.html"
    form_class=ProfileForm
    model=UserProfile
    pk_url_kwargs="id"
    success_url=reverse_lazy("profile")
    
@method_decorator(decs,name="dispatch")
class AddProfile(CreateView):
    template_name="user_profile.html"
    form_class=ProfileForm
    success_url=reverse_lazy("index")
    
    def post(self,request,*args,**kwargs):
        form=ProfileForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            profile=form.save(commit=False)
            profile.user=request.user
            profile.save()
            return redirect("index")
        else:
            return render(request,"user_profile.html",{"form":form})
@method_decorator(decs,name="dispatch")
class ViewMyProfile(TemplateView):
    template_name="user_profile.html"


    