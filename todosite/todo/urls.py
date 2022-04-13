from django.urls import path
from . import views

urlpatterns =[
    path('',views.index,name='home'),
    path('create_todo',views.create_todo,name='create_todo'),
    path('todo_detail/<int:id>',views.todo_detail,name='todo_detail'),
    path('delete_todo/<int:id>',views.delete_todo,name='delete_todo'),
    path('edit_todo/<int:id>',views.edit_todo,name='edit_todo'),
]