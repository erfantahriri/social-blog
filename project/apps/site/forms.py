from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required
from flask.ext.babel import gettext as _


class SiteForm(Form):
    title = TextField(_('Site Tile'))