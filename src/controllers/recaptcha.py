import urllib
from google.appengine.api import urlfetch

API_SSL_SERVER  ="https://api-secure.recaptcha.net"
API_SERVER      ="http://api.recaptcha.net"
VERIFY_SERVER   ="api-verify.recaptcha.net"

class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid   = is_valid
        self.error_code = error_code

def submit(recaptcha_challenge_field,
            recaptcha_response_field,
            private_key,
            remoteip):

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol')

    headers = {
               'Content-type':  'application/x-www-form-urlencoded',
               "User-agent"  :  "reCAPTCHA GAE Python"
               }

    params = urllib.urlencode ({
        'privatekey': private_key,
        'remoteip' : remoteip,
        'challenge': recaptcha_challenge_field,
        'response' : recaptcha_response_field,
        })

    httpresp = urlfetch.fetch(
                   url      = "http://%s/verify" % VERIFY_SERVER,
                   payload  = params,
                   method   = urlfetch.POST,
                   headers  = headers
                    )

    if httpresp.status_code == 200:
        # response was fine

        # get the return values
        return_values = httpresp.content.splitlines();

        # get the return code (true/false)
        return_code = return_values[0]

        if return_code == "true":
            # yep, filled perfectly
            return RecaptchaResponse (is_valid=True)
        else:
            # nope, something went wrong
            return RecaptchaResponse (is_valid=False, error_code = return_values [1])
    else:
        # recaptcha server was not reachable
        return RecaptchaResponse (is_valid=False, error_code = "recaptcha-not-reachable")

