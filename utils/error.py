class ExpirationError(Exception):
  def __init__(self, message='만기된 모임입니다.'):
    self.message = message
  
  def __str__(self):
    return 'ExpirationError: ' + self.message
    