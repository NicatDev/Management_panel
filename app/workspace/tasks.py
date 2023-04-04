from __future__ import absolute_import, unicode_literals

from datetime import datetime
from django.utils import timezone

from celery import shared_task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from account.models import Instagram
from core.models import Notification
from utils.instagram import publish_image
from workspace.models import Task, Status
from utils.notification import Notify, NotifyInstagram
from utils.instagram_bot import InstagramBOT


@shared_task(autoretry_for=(Exception,))
def notification_task(
    ref_model, ref_id, from_admin=False
):
    if settings.DEBUG or ref_model == "useractivation":
        content_type = ContentType.objects.get(model=ref_model)
        ref_model_class = content_type.model_class()
        ref_instance = ref_model_class.objects.get(pk=ref_id)
        # if not ref_instance.user:
        #     return f"User is null for {ref_instance}"

        # check if already created notification for this instance
        notification_data = {
            "ref_id": ref_instance.pk,
            "user": ref_instance.workspace.accounts.filter(type=1).first().account
        }
        event = ref_instance.get_notifyevent()
        if not event:
            return f"No active notify event found for {ref_instance}"

        notification_data["event"] = event

        notification, created = Notification.objects.get_or_create(
            **notification_data
        )

        if created or from_admin:
            # if from_admin=True send send sms
            # run notifications
            notify = Notify(ref_instance, notification)
            notify.run()

    return f"Notification successfully run for {ref_model} ID: {ref_id} !"


@shared_task(autoretry_for=(Exception,))
def notification_instagram(
    ref_model, ref_id, from_admin=False
):
    if settings.DEBUG or ref_model == "useractivation":
        content_type = ContentType.objects.get(model=ref_model)
        ref_model_class = content_type.model_class()
        ref_instance = ref_model_class.objects.get(pk=ref_id)

        # check if already created notification for this instance
        notification_data = {
            "ref_id": ref_instance.pk,
            "user": ref_instance.account
        }
        event = ref_instance.get_notifyevent()
        if not event:
            return f"No active notify event found for {ref_instance}"

        notification_data["event"] = event

        notification, created = Notification.objects.get_or_create(
            **notification_data
        )

        if created or from_admin:
            # if from_admin=True send send sms
            # run notifications
            notify = NotifyInstagram(ref_instance, notification)
            notify.run()
            print('notification run =================================================================')

    return f"Notification successfully run for {ref_model} ID: {ref_id} !"


@shared_task
def share_post_at_instagram(task_id):
    # Get the post object using the post_id
    task = Task.objects.get(id=task_id)
    client = task.client.instagram.first()
    bot = InstagramBOT()
    content_type = ContentType.objects.get_for_model(Task)
    final_status = Status.objects.filter(order=22, type=content_type).first()

    task.status = task.status.next_step
    task.save()
    # Call the share_post function
    # publish_image(task.client, task)
    if task.sharing_type == 2 and task.cover_image:
        bot.open_page()
        bot.bypass_authorization(client.username, client.password)
        result = bot.new_post(filepath=task.file.path, cover_filepath=task.cover_image.path, text=task.text)
        if result:
            task.status = final_status
            task.save()

    elif task.sharing_type == 1:
        bot.open_page()
        bot.bypass_authorization(client.username, client.password)
        result = bot.new_post(filepath=task.file.path, text=task.text)
        if result:
            task.status = final_status
            task.save()


@shared_task
def check_task_deadlines():
    # Get all tasks with a deadline less than or equal to now
    content_type = ContentType.objects.get_for_model(Task)
    status = Status.objects.filter(order=20, type=content_type).first()
    tasks = Task.objects.filter(deadline__lte=datetime.now(), status=status)

    # Determine the next deadline and set the interval accordingly
    if tasks:
        next_deadline = min(task.deadline for task in tasks)
        interval = (next_deadline - timezone.now()).total_seconds()
    else:
        interval = 180  # Default to one minute

    # Reschedule the task to run again after the interval
    check_task_deadlines.apply_async(countdown=interval)

    # Run the share_post task for each task
    for task in tasks:
        share_post_at_instagram.delay(task.id)