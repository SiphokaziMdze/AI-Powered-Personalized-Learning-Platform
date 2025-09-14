from django.shortcuts import render

def index(request):
    """Homepage view"""
    context = {
        'title': 'OSLearn AI - AI-Powered Learning Platform',
        'welcome_message': 'Master Operating Systems with AI Guidance'
    }
    return render(request, 'index.html', context)

def dashboard(request):
    """Dashboard view"""
    context = {
        'title': 'My Learning Dashboard',
        'user_progress': 65,  # Example data - replace with real data later
        'completed_lessons': 4,
        'total_lessons': 10
    }
    return render(request, 'dashboard.html', context)

