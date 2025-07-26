from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):
    """Домашняя страница Learning Log"""
    return render(request, 'learning_logs/index.html')


@login_required()
def topics(request):
    """Страница со списком тем"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required()
def topic(request, topic_id):
    """Страница с одной темой и всеми записями"""
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(topic, request)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required()
def new_topic(request):
    """Страница с новой темой"""
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required()
def new_entry(request, topic_id):
    """Страница с новой записью по конкретной теме"""
    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(topic, request)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            form.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required()
def edit_entry(request, entry_id):
    """Страница с редактированием записи"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(topic, request)

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(data=request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'topic': topic, 'form': form, 'entry': entry}
    return render(request, 'learning_logs/edit_entry.html', context)


def check_topic_owner(topic, request):
    if topic.owner != request.user:
        raise Http404


def custom_404(request, exception):
    return render(request, 'learning_logs/404.html', status=404)