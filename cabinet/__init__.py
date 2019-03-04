from flask import Flask
from flask_talisman import Talisman
app = Flask(__name__)
csp = {
    'default-src': ['\'self\'', '\'unsafe-inline\'']
}
Talisman(app, force_https=True, force_https_permanent=True, content_security_policy=csp)

import cabinet.main
import cabinet.intentions