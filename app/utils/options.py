from django.utils.translation import gettext_lazy as _


# AccountThrough type
ADMIN = 1
MEMBER = 2
CLIENT = 3
ACCOUNT_CHOICES = (
    (ADMIN, _('Admin')),
    (MEMBER, _('Member')),
    (CLIENT, _('Client')),
)

# Task sharing type
IMAGE = 1
VIDEO = 2
OTHER = 3
SHARING_TYPES = (
    (IMAGE, _("Image")),
    (VIDEO, _("Video")),
    (OTHER, _("other")),
)

STATUS_LEVELS = (
    ("base", _("Base Level")),
    ("neutral", _("Neutral Level")),
    ("work_on", _("Working on it")),
    ("final", _("Final level")),
    ("deleted", _("Deleted")),
)