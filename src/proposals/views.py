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
from .utils.db import get_or_none
from random import randint
from django.utils import timezone


def routeToErrorPage(context, request, status, message):
    context['status'] = status
    context['status_message'] = message
    return render(request, 'proposals/operationstatus.html', context)


def home(request):
    user = authenticateUser(request)
    proposals_list = Proposal.objects.order_by('vote_start_date')
    context = {
        'proposals_list': proposals_list,
        'user': user
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
            return routeToErrorPage(context, request, 'Unsuccessful',
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
        context = {
            'user': user, }
        proposal = get_or_none(Proposal, pk=proposal_id)
        if proposal == None:
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Proposal does not exist!')
        userVote = None
        if user != None:
            userVote = ProposalVote.objects.filter(
                voter_id=user.id).filter(proposal_id=proposal.id).first()

        if userVote == None:
            context['user_has_voted'] = False
            context['user_vote'] = None
        else:
            context['user_has_voted'] = True
            context['user_vote'] = userVote.vote

        votingOpen = proposal.vote_start_date < timezone.now(
        ) and timezone.now() < proposal.vote_end_date

        context['proposal'] = proposal
        context['voting_open'] = votingOpen
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
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Proposal ID not given!')
        vote = request.POST['vote']
        if vote == None:
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Vote not given!')
        proposal = Proposal.objects.get(pk=proposal_id)
        if proposal == None:
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Proposal does not exist!')
        if not (proposal.vote_start_date < timezone.now() and timezone.now() < proposal.vote_end_date):
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Voting is not open!')
        userVote = ProposalVote.objects.filter(
            voter_id=user.id).filter(proposal_id=proposal.id).first()
        if userVote != None:
            routeToErrorPage(context, request, 'Unsuccessful',
                             'Already voted!')
        newVote = ProposalVote(
            voter_id=user, proposal_id=proposal, vote=vote == 'true')
        newVote.save()

        if vote == 'true':
            proposal.yes_votes = proposal.yes_votes + 1
        else:
            proposal.no_votes = proposal.no_votes + 1
        proposal.save()

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
        print(account)
        if account == None or not checkPasswordAgainstHash(password, account.password_hash):
            return routeToErrorPage(context, request, 'Unsuccessful',
                                    'Login unsuccesful! User does not exist or incorrect password!')
        account.current_auth_token = generateAuthToken(
            username=username, randomInteger=randint(a=0, b=1000))
        account.save()
        response = HttpResponseRedirect('/proposals')
        response.set_cookie('auth_token', account.current_auth_token)
        response.set_cookie('username', account.username)
        return response
    elif request.method == 'GET':
        user = authenticateUser(request)
        if user == None:
            return render(request, 'proposals/login.html', {'user': None})

        return redirect('/proposals')


def signout(request):
    user = authenticateUser(request)
    if user == None:
        return redirect('/proposals/login')
    user.current_auth_token = None
    user.save()
    response = HttpResponseRedirect('/proposals')
    response.delete_cookie('auth_token')
    response.delete_cookie('username')
    return response


def register(request):
    if request.method == 'POST':
        user = authenticateUser(request)

        context = {
            'status': 'Success',
            'status_message': 'New account has been created!',
            'user': user
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
        user = authenticateUser(request)
        if user == None:
            return render(request, 'proposals/register.html', {'user': None})

        return redirect('/proposals')
