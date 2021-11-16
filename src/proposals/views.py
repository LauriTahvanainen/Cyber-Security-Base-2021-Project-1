from os import name
from django.db.backends import utils
from django.shortcuts import render
from django.http import HttpResponse, response, HttpResponseRedirect
from django.template import context, loader
from django.shortcuts import render, redirect
from .models import Proposal, Account, ProposalVote
from django.db import connection
from datetime import date, datetime
from .utils.auth import checkPasswordAgainstHash, generateAuthToken, hashPassword, authenticateUser
from random import randint


def routeToErrorPage(context, request, status, message):
    context['status'] = status
    context['status_message'] = message
    return render(request, 'proposals/operationstatus.html', context)


def home(request):
    proposals_list = Proposal.objects.order_by('vote_start_date')
    context = {
        'proposals_list': proposals_list
    }
    for proposal in proposals_list:
        print(proposal.vote_start_date)
    return render(request, 'proposals/index.html', context)


def create_proposal(request):
    user = authenticateUser(request)
    if user == None:
        return redirect('/proposals/login')
    if request.method == 'POST':
        context = {
            'user': user,
            'status': 'Success',
            'status_message': 'New proposal has been added!'
        }
        text = request.POST['description']
        startDate = datetime.fromisoformat(request.POST['startDate'])
        endDate = datetime.fromisoformat(request.POST['endDate'])
        if startDate > endDate:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Start date can not be after End date!')
        sql = 'INSERT INTO proposals_proposal (description, vote_start_date, vote_end_date, proposer_id, yes_votes, no_votes) VALUES ("{text}", "{startDate}", "{endDate}", "{proposer}", "0", "0");'.format(
            text=text, startDate=startDate.strftime('%Y-%m-%d %H:%M:%S'), endDate=endDate.strftime('%Y-%m-%d %H:%M:%S'), proposer=user.id)

        with connection.cursor() as cursor:
            cursor.execute(sql)
            return render(request, 'proposals/operationstatus.html', context)
    elif request.method == 'GET':
        return render(request, 'proposals/createproposal.html')


def proposal(request, proposal_id):
    if request.method == 'GET':
        user = authenticateUser(request)
        proposal = Proposal.objects.get(pk=proposal_id)
        if user != None:
            userVote = ProposalVote.objects.filter(
                voter_id=user.id).filter(proposal_id=proposal.id).first()
        context = {
            'user': user,
            'proposal': proposal,
            'user_has_voted': True if userVote != None else False,
            'user_vote': userVote.vote if userVote != None else None}
        return render(request, 'proposals/proposal.html', context)


def vote(request):
    if request.method == 'POST':
        user = authenticateUser(request)
        if user == None:
            return redirect('/proposals/login')
        context = {
            'user': user
        }
        proposal_id = request.POST['proposal_id']
        if proposal_id == None:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Proposal ID not given!')
        vote = request.POST['vote']
        if vote == None:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Vote not given!')
        proposal = Proposal.objects.get(pk=proposal_id)
        if proposal == None:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Proposal does not exist!')
        userVote = ProposalVote.objects.filter(
            voter_id=user.id).filter(proposal_id=proposal.id).first()
        if userVote != None:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Already voted!')
        newVote = ProposalVote(
            voter_id=user, proposal_id=proposal, vote=vote == 'true')
        newVote.save()

        context['status'] = 'Success'
        context['status_message'] = 'Voted!'
        context['proposal'] = proposal
        context['user'] = user
        context['user_has_voted'] = True
        context['user_vote'] = vote == 'true'
        return render(request, 'proposals/proposal.html', context)


def login(request):
    if request.method == 'POST':
        context = {
            'status': 'Success',
            'status_message': 'New account has been created!'
        }
        username = request.POST['username']
        password = request.POST['password']

        account = Account.objects.filter(username=username).first()
        if account == None or not checkPasswordAgainstHash(password, account.password_hash):
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Login unsuccesful! User does not exist or incorrect password!')
        account.current_auth_token = generateAuthToken(
            username=username, randomInteger=randint(a=0, b=1000))
        account.save()
        response = HttpResponseRedirect('/proposals')
        response.set_cookie('auth_token', account.current_auth_token)
        response.set_cookie('username', account.username)
        return response
    elif request.method == 'GET':
        return render(request, 'proposals/login.html')


def register(request):
    if request.method == 'POST':
        context = {
            'status': 'Success',
            'status_message': 'New account has been created!'
        }
        try:
            username = request.POST['username']
            password = request.POST['password']
            passwordHash = hashPassword(password)

            newAccount = Account(username=username, password_hash=passwordHash)
            newAccount.save()
            request.message = 'New account created!'
        except:
            context['status'] = 'Unsuccessful'
            context['status_message'] = 'Register unsuccessful!'
        return render(request, 'proposals/operationstatus.html', context)
    elif request.method == 'GET':
        return render(request, 'proposals/register.html')
