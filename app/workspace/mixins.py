from django.db import models


class NotificationQueryset(models.QuerySet):
    def public(self, **kwargs):
        return self.filter(**kwargs).exclude(event__web_text__exact="")


class JSONFieldModelMixin:
    def get_data(self, key=None, default=None):
        """
        Alias for get_extra
        :param key:
        :param default:
        :return:
        """

        return self.get_extra(key, default)

    def set_data(self, key=None, val=None):
        """
        Alias for set_extra
        :param key:
        :param val:
        :return:
        """

        return self.set_extra(key, val)

    def get_extra(self, key=None, default=None):
        """
        Get JSON field's value by specific `key
        :param key:
        :param default:
        :return:
        """

        if self.extra and key:
            return self.extra.get(key, default)
        return default

    def set_extra(self, key=None, val=None):
        """
        Set value of JSON field
        :param key:
        :param val:
        :return:
        """
        if key:
            if self.extra:
                self.extra[key] = val
            else:
                self.extra = {key: val}


class NotifyEventFinder:
    """
    Helper class for finding related notify event of model instance.
    See below more specific implementations:
        - StatusNotifyEventFinder
    """

    def get_notifyevent(self, **kwargs):
        from core.models import NotifyEvent

        identifier = kwargs.get("identifier", None)
        if identifier:
            return NotifyEvent.objects.filter(
                identifier=identifier, is_enabled=True
            ).last()

        raise NotImplementedError(
            f"'get_notifyevent' not implemented for {self}"
        )


class StatusNotifyEventFinder:
    """
    Helper class for detecting status related notify event of model instance.
    Can be used for all models that have 'status' foreignkey field.
    """

    def get_notifyevent(self, **kwargs):
        from core.models import NotifyEvent

        event_lookups = {
            "notify_for__model": "status",
            "notify_obj_id": self.status.pk,
        }
        return NotifyEvent.objects.filter(**event_lookups).last()
