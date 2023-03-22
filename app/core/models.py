from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
# from django.apps import apps
from ckeditor.fields import RichTextField

from workspace.mixins import JSONFieldModelMixin, NotificationQueryset


class NotifyEvent(models.Model, JSONFieldModelMixin):
    def is_ascii(self, value):
        try:
            value.encode("ascii")
        except UnicodeEncodeError as e:
            raise ValidationError(_("Please enter all your details in english characters!")) from e

    notify_for = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="+",
        limit_choices_to={
            "model__in": [
                "status",
            ],
            "app_label__in": [
                "workspace",
            ],
        },
        blank=True,
        null=True,
        verbose_name=_("Notify for"),
    )
    notify_obj_id = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("Notify object id")
    )
    notify_obj = GenericForeignKey("notify_for", "notify_obj_id")
    notification_for = models.ForeignKey(  # legacy field
        "workspace.Status",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("Notification for"),
    )
    # information
    label = models.CharField(
        max_length=100, verbose_name=_("Label")
    )
    email_subject = models.CharField(
        max_length=150, verbose_name=_("Email subject")
    )
    email_text = RichTextField()
    web_text = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("Web text"),
    )
    is_enabled = models.BooleanField(
        default=True, verbose_name=_("Notifications enabled")
    )

    extra = JSONField(
        blank=True, null=True, verbose_name=_("Extra")
    )

    # moderation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.notify_for:
            return f"{self.notify_obj}: {self.label}".capitalize()
        return f'{self.label}'.capitalize()

    def get_ref_model(self):
        if self.notify_for and self.notify_for.model == "status":
            model_class = self.notify_obj.type.model_class()
        else:
            raise ValueError("Unknown ref model for notify event")
        return model_class


class Notification(models.Model, JSONFieldModelMixin):
    # relation
    event = models.ForeignKey(
        "NotifyEvent",
        on_delete=models.SET_NULL,
        related_name="notifications",
        blank=True,
        null=True,
        verbose_name=_("Hadisə"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("İstifadəçi"),
    )

    # information
    ref_id = models.CharField(
        max_length=150, verbose_name=_("Referans Nömrəsi")
    )
    is_read = models.BooleanField(
        default=False, verbose_name=_("Oxunub")
    )
    extra = JSONField(
        blank=True, null=True, verbose_name=_("Extra")
    )

    # moderation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotificationQueryset.as_manager()

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.user}: {self.event}"

    def __get_text_kwargs_(self):
        event_obj = self.get_ref_obj()
        try:
            kwargs_dict = {
                "user_full_name": event_obj.account.get_full_name(),
                "user_email": event_obj.account.email,
            }
        except Exception:
            kwargs_dict = {
                "user_full_name": event_obj.user.get_full_name(),
                "user_email": event_obj.user.email,
            }
        return kwargs_dict

    def get_ref_obj(self):
        event_model = self.event.get_ref_model()
        return event_model.objects.get(pk=self.ref_id)

    @property
    def preview_text(self):
        """
        For serializers
        :return:
        """
        web_text = ""

        if self.event and self.event.web_text:
            web_text = self.event.web_text.format(**self.__get_text_kwargs_())

        return web_text

    @property
    def preview_email_subject(self):
        return self.event.email_subject.format(**self.__get_text_kwargs_())

    @property
    def preview_email_text(self):
        if self.event and self.event.email_text:
            return self.event.email_text
        return self.event.web_text

    # @property
    # def preview_url(self):
    #     event_obj = self.get_ref_obj()
    #     model_name = event_obj.__class__.__name__.lower()
    #     return "{}{}s".format(reverse("dashboard-page"), model_name)