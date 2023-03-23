# from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
# from django.db import transaction
# from django.db.models.signals import post_save
# from django.db.models.signals import pre_delete
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
#
# from workspace.models import Status, Task
# from workspace.tasks import notification_task
#
# # DB transaction decorator
# def on_transaction_commit(func):
#     def inner(*args, **kwargs):
#         transaction.on_commit(lambda: func(*args, **kwargs))
#     return inner
#
#
# @receiver(post_save, sender=Task, dispatch_uid="handle_task_changes")
# @on_transaction_commit
# def handle_task_changes(sender, **kwargs):
#     task = kwargs.get("instance")
#     created = kwargs.get("created")
#     # if task created, then set base level status
#     if created and task.status is None:
#         # content_type = ContentType.objects.get_for_model(Task)
#         status = Status.objects.get(level="base")
#         task.status = status
#         task.save()
#
#     # final_status = Status.objects.task_statuses().get(level="final")
#
#     # if status changed create notification
#     if task.cache_status_id != task.status_id:
#         notification_task.delay("task", task.pk)
