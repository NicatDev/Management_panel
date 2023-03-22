from html import unescape
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from app import settings
from workspace.models import AccountThrough, Deadline


class Notify(object):
    obj = None
    notifications = None

    def __init__(self, obj, notification, **kwargs):
        """
        :param obj: <Task> instance
        """
        self.obj = obj
        self.notification = notification

    def __send__email(self, ref_obj):
        message = f"""
                        Taskın adı:                     {ref_obj.title}             
                        Mətn:                           {unescape(self.notification.preview_email_text)}             
        """
        send_mail(
            subject='Bildiriş',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['arifogluisa@gmail.com']
            )

    
    def __send_out__(self):
        ref_obj = self.notification.get_ref_obj()
        self.__send__email(ref_obj)

    def send(self):
        """
        Send out the notifications to the user
        :return:
        """
        if self.notification:
            self.__send_out__()

    def save_notification_content(self):
        """
        Saves sent notification content to 'extra' field. Just matter of proof.
        """
        if self.notification and self.notification.pk:
            notification = self.notification
            notification.extra = notification.extra or {}
            notification.extra.update(
                {
                    "text": notification.preview_text,
                    # "sms_text": notification.preview_sms_text,
                    "email_subject": notification.preview_email_subject,
                    "email_text": notification.preview_email_text,
                }
            )
            notification.save(update_fields=["extra"])

    def run(self):
        """
        Sending notification
        :return:
        """
        self.send()
        self.save_notification_content()


class NotifyInstagram(object):
    obj = None
    notifications = None

    def __init__(self, obj, notification, **kwargs):
        """
        :param obj: <Instagram> instance
        """
        self.obj = obj
        self.notification = notification

    def __send__email(self, ref_obj):
        message = f"""
                        Taskın adı:                     {self.notification.preview_email_subject}             
                        Mətn:                           {unescape(self.notification.preview_email_text)}             
        """
        send_mail(
            subject='Bildiriş',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['arifogluisa@gmail.com']
        )

    def __send_out__(self):
        ref_obj = self.notification.get_ref_obj()
        self.__send__email(ref_obj)

    def send(self):
        """
        Send out the notifications to the user
        :return:
        """
        if self.notification:
            self.__send_out__()

    def save_notification_content(self):
        """
        Saves sent notification content to 'extra' field. Just matter of proof.
        """
        if self.notification and self.notification.pk:
            notification = self.notification
            notification.extra = notification.extra or {}
            notification.extra.update(
                {
                    "text": notification.preview_text,
                    # "sms_text": notification.preview_sms_text,
                    "email_subject": notification.preview_email_subject,
                    "email_text": notification.preview_email_text,
                }
            )
            notification.save(update_fields=["extra"])

    def run(self):
        """
        Sending notification
        :return:
        """
        self.send()
        self.save_notification_content()