from django.db import models

class Proposal(models.Model):
  description = models.CharField(max_length=1000)
  vote_start_date= models.DateTimeField('date voting starts')
  vote_end_date= models.DateTimeField('date voting ends')


