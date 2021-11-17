LINK: https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1
The application is a platform for creating proposal and then voting on those proposals.

## Installation
The project is a Python Django web application. To run the app locally:

1. Install python3 and all the necessary Django libraries.

2. Clone the repository

3. Cd to src/ where the manage.py file is located

4. In that folder run: python3 manage.py migrate to ready the database

5. In the same folder run python3 manage.py runserver to run the app

6. The app starts by default at http://127.0.0.1:8000

7. The homepage is at http://127.0.0.1:8000/proposals/

## FLAW 1:
#### [A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)

### Source
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L136

### Description
*"Bypassing access control checks by modifying the URL (parameter tampering or force browsing), internal application state, or the HTML page, or by using an attack tool modifying API requests." -OWASP

*"Force browsing to authenticated pages as an unauthenticated user or to privileged pages as a standard user."* -OWASP

The view should return all proposals that the signed in user has voted on with the vote given by the user.
But because the votes are fetched with a parameter that is given in the url, anyone can access anyones votes by using this view, without even being signed in.
The handler starts with a line: 
```  
user = authenticateUser(request)
```
But this does not actually check for authentication.

### Fix
There is a ready made authentication util, which returns the signed in user. It should be used, and it should be used correctly.

Checking for if a user is signed in can be done with:

```  
user = authenticateUser(request)
if user == None:
  return redirect('/proposals/login')
```  

This user object should be used to get fetch the votes, since it has been accessed with server side authentication, which can be trusted. The user_id will not be given as a parameter and thus we accomplish correct access to the votes only by signed in users:

```  
def proposals_voted_on(request):
    if request.method == 'GET':
        user = authenticateUser(request)
        if user == None:
            return redirect('/proposals/login')
        context = {
          'user': user
        }

        userVotes = ProposalVote.objects.select_related('proposal_id').filter(voter_id=user.id).all()

        context['user_votes'] = userVotes
        return render(request, 'proposals/voted.html', context)
```  


## FLAW 2:

### Source

### Description

### Fix


## FLAW 3:

### Source

### Description

### Fix


## FLAW 4:

### Source

### Description

### Fix


## FLAW 5:

### Source

### Description

### Fix

