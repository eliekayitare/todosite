from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import todo
from .models import Todo

# Create your views here.

# def get_showing_todo(request,todos):
#     if request.GET and request.GET.get('filter'):
#         if request.GET.get('filter')=='complete':
#             return todos.filter(is_completed=True)
#         if request.GET.get('filter')=='incomplete':
#             return todos.filter(is_completed=False)
#         return todos

@login_required
def index(request):
    todos=Todo.objects.filter(owner=request.user)
    context ={"todos":todos,"completed_count":todos.filter(is_completed=True).count(),
    "incompleted_count":todos.filter(is_completed=False).count(),"all_count":todos.count()}

    return render(request,'todo/index.html',context)

@login_required
def create_todo(request):

    if request.method=='POST':
        title=request.POST.get('title')
        description=request.POST.get('description')
        is_completed=request.POST.get('is_completed', False)

        if is_completed=="on":
            is_completed=True
        else:
            is_completed=False
        
        Todo.objects.create(title=title,description=description,is_completed=is_completed,owner=request.user)
        messages.add_message(request,messages.SUCCESS,"Todo created successfully")
        return redirect('home')
    else:
        return render(request,'todo/create_todo.html')
@login_required
def todo_detail(request,id):
    todo_detail=Todo.objects.get(id=id)
    return render(request,'todo/todo_detail.html',{'todo_detail':todo_detail})
@login_required
def delete_todo(request,id):
    todos=Todo.objects.get(id=id)
    if request.method=="POST":
        if todos.owner==request.user:

            todos.delete()
            messages.add_message(request,messages.SUCCESS,"Todo deleted")
            return redirect('home')
        return render(request,'todo/delete_todo.html',{'todos':todos})

    # todo_detail=get_object_or_404(Todo,pk)
    return render(request,'todo/delete_todo.html',{'todos':todos})

@login_required
def edit_todo(request,id):
    todo=Todo.objects.get(id=id)
    if request.method=="POST":
        # title=request.POST['title']
        # description=request.POST['description']
        # is_completed=request.POST['is_completed']
        title=request.POST.get('title')
        description=request.POST.get('description')
        is_completed=request.POST.get('is_completed',False)

        
        todo.title=title
        todo.description=description
        if is_completed=="on":
            is_completed=True
           
        else:
            is_completed=False
        
        if todo.owner==request.user:
    
            todo.save()
            messages.add_message(request,messages.SUCCESS,"Todo updated successfully")
            return redirect('home')
        return render(request,'todo/edit_todo.html',{'todo':todo})

    return render(request,'todo/edit_todo.html',{'todo':todo})
