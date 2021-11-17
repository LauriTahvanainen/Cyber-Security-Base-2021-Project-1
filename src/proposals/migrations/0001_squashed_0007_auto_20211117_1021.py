# Generated by Django 3.2.7 on 2021-11-17 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('proposals', '0001_initial'), ('proposals', '0002_auto_20211109_1123'), ('proposals', '0003_auto_20211109_1212'), ('proposals', '0004_alter_account_username'), ('proposals', '0005_auto_20211116_1257'), ('proposals', '0006_auto_20211116_1455'), ('proposals', '0007_auto_20211117_1021')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=1000, unique=True)),
                ('password_hash', models.CharField(max_length=1000)),
                ('current_auth_token', models.CharField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('vote_start_date', models.DateTimeField(verbose_name='date voting starts')),
                ('vote_end_date', models.DateTimeField(verbose_name='date voting ends')),
                ('proposer', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='proposals.account')),
            ],
        ),
        migrations.CreateModel(
            name='ProposalVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.BooleanField(default=False)),
                ('proposal_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='proposals.proposal')),
                ('voter_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='proposals.account')),
            ],
        ),
        migrations.AddConstraint(
            model_name='proposalvote',
            constraint=models.UniqueConstraint(fields=('voter_id', 'proposal_id'), name='One User One Vote'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='no_votes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='proposal',
            name='yes_votes',
            field=models.IntegerField(default=0),
        ),
    ]
