from wtforms import StringField
from wtforms.validators import DataRequired

from selene import constants
from selene.base import BaseForm


class SiteSettingsForm(BaseForm):
    title = StringField(validators=[DataRequired(constants.TITLE_IS_REQUIRED)])
    slogan = StringField()
