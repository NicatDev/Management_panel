from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from workspace.models import WorkSpace

@login_required
def index(request):
    return render(request, 'home/index.html')
