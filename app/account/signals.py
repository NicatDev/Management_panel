from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Instagram, SocialPlatform
from workspace.models import Status
from workspace.tasks import notification_instagram


# DB transaction decorator
def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))
    return inner


@receiver(post_save, sender=Instagram, dispatch_uid="handle_instagram_changes")
@on_transaction_commit
def handle_instagram_changes(sender, **kwargs):
    insta = kwargs.get("instance")
    created = kwargs.get("created")
    # if task created, then set base level status
    if created and insta.status is None:
        content_type = ContentType.objects.get_for_model(Instagram)
        status = Status.objects.get(level="base", type=content_type)
        insta.status = status
        insta.save()
        SocialPlatform.objects.get_or_create(account=insta.account, instagram=insta)

    # final_status = Status.objects.task_statuses().get(level="final")

    # if status changed create notification
    if insta.cache_status_id != insta.status_id:
        notification_instagram.delay("instagram", insta.pk)