from django.db import models
from django.db.models import constraints

# from django.contrib.auth.models import User


class Account(models.Model):
    username = models.CharField(max_length=1000, unique=True)
    password_hash = models.CharField(max_length=1000)
    current_auth_token = models.CharField(max_length=1000, null=True)


class Proposal(models.Model):
    description = models.CharField(max_length=1000)
    vote_start_date = models.DateTimeField('date voting starts')
    vote_end_date = models.DateTimeField('date voting ends')
    proposer = models.ForeignKey(Account, on_delete=models.CASCADE)
    yes_votes = models.IntegerField(default=0)
    no_votes = models.IntegerField(default=0)


class ProposalVote(models.Model):
    voter_id = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    proposal_id = models.ForeignKey(Proposal, on_delete=models.DO_NOTHING)
    vote = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter_id', 'proposal_id'], name='One User One Vote')
        ]
