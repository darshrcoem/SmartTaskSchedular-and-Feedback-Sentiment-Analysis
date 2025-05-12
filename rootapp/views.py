from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm
from .utils import predict_sentiment

def index(request):
    return render(request, 'index.html')

def select_role(request):
    role = request.GET.get('role')
    if role == 'admin':
        return redirect('admin_dashboard')
    return redirect('user_dashboard')  # You can handle user dashboard separately

def admin_dashboard(request):
    return render(request, 'admin.html')

def batch_tasks(request, batch_id):
    tasks = Task.objects.filter(batch=batch_id)
    form = TaskForm()
    return render(request, 'batch.html', {'tasks': tasks, 'form': form, 'batch_id': batch_id})

def add_task(request, batch_id):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.batch = batch_id
            task.save()
            return redirect('batch_tasks', batch_id=batch_id)
    return redirect('batch_tasks', batch_id=batch_id)

from django.shortcuts import get_object_or_404

# User dashboard view
def user_dashboard(request):
    user_tasks = Task.objects.filter(created_by='user')
    admin_tasks = Task.objects.filter(created_by='admin')

    combined_tasks = user_tasks.union(admin_tasks)
    # schedule = optimize_schedule(combined_tasks)

    # Check if the schedule is empty


    return render(request, 'user.html', {
        'user_tasks': user_tasks,
        'admin_tasks': admin_tasks,
        # 'schedule': schedule
    })

# View tasks in batch for user
def user_batch_tasks(request, batch_id):
    admin_tasks = Task.objects.filter(batch=batch_id, created_by='admin')
    user_tasks = Task.objects.filter(batch=batch_id, created_by='user')
    form = TaskForm()
    return render(request, 'user_batch.html', {
        'admin_tasks': admin_tasks,
        'user_tasks': user_tasks,
        'form': form,
        'batch_id': batch_id
    })

# User adds task
def user_add_task(request, batch_id):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.batch = batch_id
            task.created_by = 'user'
            task.save()
    return redirect('user_batch_tasks', batch_id=batch_id)

# User updates their own task
def user_update_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.created_by != 'user':
        return redirect('user_batch_tasks', batch_id=task.batch)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('user_batch_tasks', batch_id=task.batch)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'update_task.html', {'form': form, 'task': task})

def admin_update_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.created_by != 'admin':
        return redirect('admin_dashboard')  # Restrict to admin tasks only

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('batch_tasks', batch_id=task.batch)
    else:
        form = TaskForm(instance=task)

    return render(request, 'update_task.html', {'form': form, 'task': task})

from django.shortcuts import get_object_or_404, redirect

from .models import Task
from .utils import optimize_schedule

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    # Restrict deletion to the creator of the task
    if task.created_by == 'admin':
        redirect_url = 'admin_dashboard'
    elif task.created_by == 'user':
        redirect_url = 'user_batch_tasks'
    else:
        return redirect('index')  # Fallback in case of invalid creator

    if request.method == 'POST':
        task.delete()
        if task.created_by == 'user':
            return redirect(redirect_url, batch_id=task.batch)
        return redirect(redirect_url)

    return render(request, 'confirm_delete.html', {'task': task})

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    # Restrict deletion to the creator of the task
    if task.created_by == 'admin':
        redirect_url = 'admin_dashboard'
    elif task.created_by == 'user':
        redirect_url = 'user_batch_tasks'
    else:
        return redirect('index')  # Fallback in case of invalid creator

    if request.method == 'POST':
        task.delete()
        if task.created_by == 'user':
            return redirect(redirect_url, batch_id=task.batch)
        return redirect(redirect_url)

    return render(request, 'confirm_delete.html', {'task': task})

from datetime import date

def optimize(request):
    today = date.today()

    # Mark overdue tasks as completed
    Task.objects.filter(deadline__lt=today, status='pending').update(status='completed')

    # Pass only pending tasks to the optimizer
    tasks = Task.objects.filter(status='pending')

    schedule = optimize_schedule(tasks)  # Your optimization logic

    return render(request, 'optimize.html', {'schedule': schedule})

from datetime import date

today = date.today()

def completed_tasks(request):
    completed = Task.objects.filter(status='completed')
    Task.objects.filter(deadline__lt=today, status='pending').update(status='completed')
    return render(request, 'completed_tasks.html', {'completed_tasks': completed})

def user_delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home')) 
    

 # Redirects to previous page

def mark_task_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'completed'
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirects to the same page


def scheduled_tasks(request):
    today = date.today()
    tasks = Task.objects.filter(date__gt=today, status='pending')
    return render(request, 'scheduled_tasks.html', {'tasks': tasks})

def ongoing_tasks(request):
    today = date.today()
    tasks = Task.objects.filter( date__lte=today, deadline__gte=today, status='pending')
    return render(request, 'ongoing_tasks.html', {'tasks': tasks})

from django.http import JsonResponse
from django.http import JsonResponse

def predict_emotion(request):
    sample_text = "I love spending time with my friends!"
    sentiment = predict_sentiment(sample_text)
    return JsonResponse({'text': sample_text, 'predicted_sentiment': sentiment})

#from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
#from .models import Task  # Assuming Task is the model for tasks

def submit_feedback(request, task_id):
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        task = get_object_or_404(Task, id=task_id)
        task.feedback = feedback  # Assuming the Task model has a feedback field
        task.save()
        predicted_emotion = predict_sentiment(feedback)  # Assuming predict_sentiment returns the emotion
        task.emotion = predicted_emotion  # Assuming the Task model has an emotion field
        task.save()
        return redirect('completed_tasks')  # Redirect back to the completed tasks page
    return HttpResponse("Invalid request", status=400)

from collections import defaultdict

def conflicting_tasks(request):
    tasks = Task.objects.all()
    time_map = defaultdict(list)

    # Group tasks by (date, time)
    for task in tasks:
        key = (task.date, task.time)
        time_map[key].append(task)

    # Only include entries where more than one task shares the same (date, time)
    conflicting_tasks = []
    for task_group in time_map.values():
        if len(task_group) > 1:
            conflicting_tasks.extend(task_group)

    return render(request, 'conflict.html', {'conflicting_tasks': conflicting_tasks})

from collections import Counter

from collections import Counter
from django.shortcuts import render
from .models import Task
import json

from django.shortcuts import render
from .models import Emotion, Task

def feedback_results(request):
    # Reset counts for demo purposes (optional)
    Emotion.objects.all().update(count=0)

    tasks = Task.objects.exclude(emotion__isnull=True)
    for task in tasks:
        if task.emotion:
            emotion_obj, created = Emotion.objects.get_or_create(name=task.emotion)
            emotion_obj.count += 1
            emotion_obj.save()

    emotions = Emotion.objects.all()
    emotion_counts = {e.name: e.count for e in emotions}

    return render(request, 'feedbackres.html', {'emotion_counts': emotion_counts})