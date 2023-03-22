from django.contrib import admin

from .forms import NotifyEventForm
from .models import NotifyEvent, Notification


@admin.register(NotifyEvent)
class NotifyEventAdmin(admin.ModelAdmin):
    # change_list_template = "admin/notifyevent/change_list.html"
    form = NotifyEventForm

    list_display = (
        "label",
        "get_event_content_type",
        "is_enabled",
    )
    list_filter = ("notify_for",)

    def get_event_content_type(self, obj):
        ref_model = obj.get_ref_model()
        if ref_model:
            return ref_model.__name__

    get_event_content_type.admin_order_field = "notification_for__type"
    get_event_content_type.short_description = "Content Type"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    # actions = ["delete_selected"]
    search_fields = ("user__email",)
    list_filter = ("event",)
    list_display = (
        "__str__",
        "get_notification_content_type",
        "get_notification_ref_obj",
        "created_at",
    )

    def get_notification_content_type(self, obj):
        return obj.event.get_ref_model()._meta.model_name

    # get_notification_content_type.admin_order_field = 'notification_for__type'
    get_notification_content_type.short_description = "Content Type"

    def get_notification_ref_obj(self, obj):
        return obj.get_ref_obj()

    # get_notification_ref_obj.admin_order_field = 'event__notification_for__type'
    get_notification_ref_obj.short_description = "Referred to"