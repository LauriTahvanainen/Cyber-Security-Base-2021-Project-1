from django.shortcuts import render
from django.http import HttpResponse
from django.template import context, loader
from django.shortcuts import render
from .models import Proposal


def home(request):
    proposals_list = Proposal.objects.order_by('-vote_start_date')
    context = {
        'proposals_list': proposals_list
    }
    return render(request, 'votes/index.html', context)


def create_proposal(request):
    if request.method == 'POST':
        return HttpResponse('NO')
    elif request.method == 'GET':
        return render(request, 'votes/createproposal.html')
