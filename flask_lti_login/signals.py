from blinker import Namespace

signals = Namespace()

lti_login_authenticated = signals.signal('lti-login-authenticated')