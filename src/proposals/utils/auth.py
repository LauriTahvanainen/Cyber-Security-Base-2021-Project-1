import hashlib
import datetime

from proposals.models import Account

def hashPassword(password: str):
    hash = hashlib.md5(password.encode()).hexdigest()
    return hash


def checkPasswordAgainstHash(password: str, hash: str):
    return hashPassword(password) == hash


def generateAuthToken(username: str, randomInteger):
  return username + str(int(datetime.datetime.now().timestamp())) + str(randomInteger)

def authenticateUser(request):
  if 'username' in request.COOKIES and 'auth_token' in request.COOKIES:
      username = request.COOKIES['username']
      auth_token = request.COOKIES['auth_token']
      user = Account.objects.filter(username=username).filter(current_auth_token=auth_token).first()
      return user
  else:
    return None