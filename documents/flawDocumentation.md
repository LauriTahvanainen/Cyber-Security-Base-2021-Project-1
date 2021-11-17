LINK: https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1
The application is a platform for creating proposals and then users voting on those proposals.

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
#### [A07:2021 – Identification and Authentication Failures ](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

### Source
Login:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L149

Register:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L190

Signout:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L178

Example of authentication:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L91

Implementation of Authentication:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/utils/auth.py#L18

Account model:
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/models.py#L7


### Description
The authentication is implemented by writing it from scratch. Passwords are saved in the database as unsalted md5 hashes. When user logs in, an authentication token is saved to the database and sent to the user as an cookie. After that, authentication can be done with two cookies 'auth_token' and 'username'. The authentication token is of the following form: 

```
 return username + str(int(datetime.datetime.now().timestamp())) + str(randomInteger)
```

Following the OWASP description on this vulnerability category, the implemented authentication has the following weaknesses:

The system accept any password, as short or common as possible.

The login could be brute forced, there is no system against that.

The hash is unsalted and weak, thus easy to crack by brute force.

There is no multifactor authentication.

The authentication token does not expire. Only reset when user signs out

Some attacks against this authentication system thus are:
One can brute force a login quite easily with some automated sign in program. If an attacker knows an username, and when approximately the user signed in, it is very easy to brute force a correct authentication token. Thus the attacker can bypass brute forcing the login. When the attacker manages to get the token, it can be used to until the user signs out.

### Fix
Code examples for this fix from [here](https://docs.djangoproject.com/en/3.2/topics/auth/default/)

The vulnerability can be fixed easily, by using an existing authentication library. In this case, django has a ready made system for authentication and authorization.

Some changes would be that we would use the User object, instead of the self created Account object.
Django handles safe password hashing using salting. Creating a new user is as easy as:

```
user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
```
There is also session handling using cookies ready made to be used. Using the library is quite similar to the self made system:

```
if request.user.is_authenticated:
    # Do something for authenticated users.
    ...
else:
    # Do something for anonymous users.
    ...
```

The library also has group management. 

By using the library correctly, all the above mentioned vulnerabilities can be fixed.



## FLAW 3:
#### [A03:2021 – Injection ](https://owasp.org/Top10/A03_2021-Injection/)

### Source
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/views.py#L50

### Description
Using raw SQL, in this case leads to an SQL injection.
For example by giving this proposal description when creating a new proposal:

*Is hacking evil?", "2000-12-12 12:12:00+00:00", "2033-12-12 12:12:00+00:00", 1, 1000, 10);--*

An attacker can create a proposal with any amount of yes votes, in this case 1000. An attacker can even insert someone else as the creator of the proposal.


### Fix
The problem is fixed by using the django ORM, which protects against SQL-injection:

```
newProposal = Proposal(text = text, vote_start_date = startDate, vote_end_date = endDate, proposer_id = user.id)
newProposal.save()
```

If one still needs to use raw SQL, the sanitazion of all the given parameters should be done properly.

## FLAW 4:
#### [A02:2021 – Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

### Source
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/utils/auth.py#L7

### Description
The self-made authentication system does not use cryptographically strong enough of a hashing function for the passwords. The implementation uses the MD5 algorithm, which is not considered safe anymore. An 8 character password can be cracked in a handful of minutes. 
Also, the password are not salted. Not using salting makes the already weak hashes vulnerable to attacks that use precomputed tables of passwords and hashes.
### Fix
The system should use a safe hashing function such as SHA-3 with random salting. The salt should be long, in case of SHA-3 atleast 256 bits.

## FLAW 5:
#### [A02:2021 – Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

### Source
https://github.com/LauriTahvanainen/Cyber-Security-Base-2021-Project-1/blob/main/src/proposals/utils/auth.py#L7

### Description

### Fix

