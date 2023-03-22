from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

from utils.abstract_models import AbstractBaseModel
from workspace.mixins import StatusNotifyEventFinder


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class Account(AbstractUser):
    username = models.CharField(_('username'), max_length=255, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True, null=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='profile_pictures', null=True, blank=True)
    description = models.TextField(_('description'), null=True, blank=True)
    company = models.CharField(_('company'), max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("account")
        verbose_name_plural = _("accounts")

    def __str__(self):
        return self.get_full_name()


class SocialPlatform(models.Model):
    account = models.ForeignKey(
        'account.Account',
        on_delete=models.CASCADE,
        related_name='social_platforms',
        verbose_name=_('account'),
    )
    instagram = models.OneToOneField(
        'account.Instagram',
        related_name='social_platforms',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.account}'

    class Meta:
        verbose_name = _("Social platform")
        verbose_name_plural = _("Social platforms")


class Instagram(AbstractBaseModel, StatusNotifyEventFinder):
    account = models.ForeignKey(
        Account,
        related_name='instagram',
        on_delete=models.CASCADE,
        verbose_name=_('account')
    )
    username = models.CharField(
        _('username'),
        max_length=820,
    )
    password = models.CharField(
        _('password'),
        max_length=820,
    )
    twoFA = models.BooleanField(
        _('2FA'),
        default=False
    )
    twoFACode = models.CharField(
        _('2FA Code'),
        max_length=255,
        null=True,
        blank=True
    )
    session_id = models.CharField(
        _('session ID'),
        max_length=255,
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        "workspace.Status",
        verbose_name=_("Status"),
        on_delete=models.DO_NOTHING,
        related_name="instagram_accounts",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.account.get_full_name()}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_status_id = self.status_id

    class Meta:
        verbose_name = _("Instagram")
        verbose_name_plural = _("Instagram")
