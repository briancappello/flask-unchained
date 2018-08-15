import blinker


signals = blinker.Namespace()

user_registered = signals.signal('user-registered')

user_confirmed = signals.signal('user-confirmed')

confirm_instructions_sent = signals.signal('confirm-instructions-sent')

login_instructions_sent = signals.signal('login-instructions-sent')

password_reset = signals.signal('password-reset')

password_changed = signals.signal('password-changed')

reset_password_instructions_sent = signals.signal('password-reset-instructions-sent')
