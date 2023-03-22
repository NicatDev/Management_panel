from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from core.models import NotifyEvent


class NotifyEventForm(forms.ModelForm):
    notify_obj_id = forms.ChoiceField(required=False)

    class Meta:
        model = NotifyEvent
        exclude = ("notify_for", "notification_for")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notify_obj_id"].choices = self._get_notify_obj_choices()
        self.fields["notify_obj_id"].label = "Notification for"
        self.initial["notify_obj_id"] = self._get_notify_obj_initial()

    def _get_notify_obj_choices(self):
        from workspace.models import Status

        blank_choice = [(None, "-----------")]
        status_choices = [
            (f"workspace__status__{obj.pk}", f"STATUS: {obj}")
            for obj in Status.objects.filter(
                Q(type__model__in=["task"]) | Q(type__model__in=["instagram"])
            )
        ]

        return blank_choice + status_choices

    def _get_notify_obj_initial(self):
        if self.instance and self.instance.notify_obj:
            obj = self.instance.notify_obj
            return f"{obj._meta.app_label}__{obj._meta.model_name}__{obj.pk}"

    def _prep_notify_for_and_obj_id(self):
        _notify_obj_id = self.data.get("notify_obj_id", None)
        if _notify_obj_id:
            values = _notify_obj_id.split("__")
            try:
                model_class = apps.get_model(values[0], values[1])
                notify_for = ContentType.objects.get_for_model(model_class)
                notify_obj_id = values[2]
            except (IndexError, LookupError):
                raise forms.ValidationError(
                    _("Invalid notify obj id"), code="invalid"
                )

            return {"notify_for": notify_for, "notify_obj_id": notify_obj_id}

        return _notify_obj_id or None

    def clean_notify_obj_id(self):
        notify_obj_id = self._prep_notify_for_and_obj_id()
        if isinstance(notify_obj_id, dict):
            return notify_obj_id.get("notify_obj_id")
        return notify_obj_id

    def clean(self):
        cleaned_data = super().clean()
        # both of them should not be null
        if not cleaned_data.get("notify_obj_id") and not cleaned_data.get(
            "identifier"
        ):
            raise forms.ValidationError(
                _(
                    "Either notification for or identifier must be supplied"
                ),
                code="invalid",
            )
        # although one of them should be null
        if cleaned_data.get("notify_obj_id") and cleaned_data.get(
            "identifier"
        ):
            raise forms.ValidationError(
                _(
                    "Both notificaton for and identifier can not be set at the same time"
                ),
                code="invalid",
            )
        return cleaned_data

    def save(self, commit=True):
        values = self._prep_notify_for_and_obj_id()
        if values:
            notify_for = values.get("notify_for")
            self.instance.notify_for = notify_for

        return super().save(commit)