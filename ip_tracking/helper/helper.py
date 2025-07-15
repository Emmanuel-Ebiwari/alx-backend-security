def check_user_consent(request):
  if request.user.is_consented: # this is only an example.
    return True
  return False