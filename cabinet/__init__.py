from flask import Flask
from flask_talisman import Talisman
from flask_login import LoginManager

app = Flask(__name__, subdomain_matching=True)
app.config.from_pyfile('cabinet.cfg')
csp = {
    'default-src': ['\'self\'', app.config['SERVER_NAME'], '*.' + app.config['SERVER_NAME'], '\'unsafe-inline\'']
}
Talisman(app, force_https=True, force_https_permanent=True, content_security_policy=csp)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = None
login_manager.init_app(app)

import cabinet.main