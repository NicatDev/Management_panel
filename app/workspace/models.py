import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from ckeditor.fields import RichTextField
from utils.abstract_models import AbstractBaseModel
from workspace.mixins import JSONFieldModelMixin, StatusNotifyEventFinder
from utils.options import ACCOUNT_CHOICES, ADMIN, SHARING_TYPES, IMAGE, STATUS_LEVELS


class AccountThrough(AbstractBaseModel):
    account = models.ForeignKey(
        'account.Account',
        related_name='workspace',
        on_delete=models.SET_NULL,
        null=True
    )
    workspace = models.ForeignKey(
        'workspace.WorkSpace',
        related_name='accounts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    type = models.IntegerField(choices=ACCOUNT_CHOICES, default=ADMIN)
    # def __str__(self):
    #     return self.account.get_full_name()

    class Meta:
        verbose_name = _("Account Through")
        verbose_name_plural = _("Account Through")


class WorkSpace(AbstractBaseModel):
    title = models.CharField(
        _("title"),
        max_length=255,
    )
    account = models.ManyToManyField(
        'account.Account',
        through='workspace.AccountThrough',
        related_name='workspaces'
    )
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        unique=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(WorkSpace, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("WorkSpace")
        verbose_name_plural = _("WorkSpaces")


class Task(AbstractBaseModel, StatusNotifyEventFinder):
    workspace = models.ForeignKey(
        'workspace.WorkSpace',
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    title = models.CharField(
        _("title"),
        max_length=255,
    )
    description = models.TextField(
        _('description'),
        null=True,
        blank=True,
    )
    text = RichTextField(
        _('sharing text'),
        null=True,
        blank=True,
    )
    file = models.FileField(
        _('file'),
        null=True,
        blank=True,
        upload_to='task_files'
    )
    cover_image = models.ImageField(
        _('cover image'),
        null=True,
        blank=True,
        upload_to='task_cover_images'
    )
    client = models.ForeignKey(
        'account.Account',
        on_delete=models.CASCADE,
        related_name='client_tasks',
        verbose_name=_('client'),
        db_index=True,
        null=True,
        blank=True,
    )
    sharing_platform = models.ManyToManyField(
        'account.SocialPlatform',
        related_name='used_in_tasks',
        verbose_name=_('sharing platform'),
        blank=True,
    )
    sharing_type = models.IntegerField(
        _('sharing type'),
        choices=SHARING_TYPES,
        default=IMAGE,
    )
    assignee = models.ManyToManyField(
        "account.Account",
        through='workspace.Deadline',
        related_name="assigned_tasks",
        verbose_name=_("assignee"),
        blank=True,
    )
    status = models.ForeignKey(
        "workspace.Status",
        verbose_name=_("Status"),
        on_delete=models.DO_NOTHING,
        related_name="tasks",
        null=True,
        blank=True,
    )
    deadline = models.DateTimeField(
        _('deadline'),
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        unique=True,
        blank=True
    )

    @property
    def time_till_deadline(self):
        from django.utils import timezone
        now = timezone.now()
        res = self.deadline - now
        return int(res.days)

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # cache current state of instance
        # self.cache_instance = model_to_dict(self)
        self.cache_status_id = self.status_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Task, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")


class TaskFile(AbstractBaseModel):
    task = models.ForeignKey(
        Task,
        related_name='files',
        on_delete=models.CASCADE
    )
    file = models.FileField(
        _('file'),
    )

    def __str__(self):
        return f'{self.task.title}'

    # def save(self, *args, **kwargs):
    #     if not self.file:
    #         return super().save(*args, **kwargs)
    #
    #     # Get the filename and extension of the uploaded file
    #     filename, ext = os.path.splitext(self.file.name)
    #
    #     # Construct the new file path with the task ID included
    #     new_path = f'files/task/{self.task.id}/{filename}{ext}'
    #
    #     # Set the file path and save the model
    #     self.file.name = new_path
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Task File")
        verbose_name_plural = _("Task Files")


class Status(AbstractBaseModel, JSONFieldModelMixin):
    type = models.ForeignKey(
        ContentType,
        verbose_name=_("Statusun Tipi"),
        on_delete=models.DO_NOTHING,
        related_name="+",
        limit_choices_to={
            "model__in": [
                "task",
                "instagram"
            ],
            "app_label__in": ["workspace", "account"],
        },
        null=True,
    )
    next_step = models.ForeignKey(
        "self",
        verbose_name=_("Next step"),
        blank=True,
        null=True,
        related_name="previous_steps",
        on_delete=models.DO_NOTHING,
    )
    name = models.CharField(
        _('name'),
        max_length=50,
        null=True,
        blank=True,
    )
    order = models.IntegerField(
        _('order'),
        default=0,
    )
    level = models.CharField(
        max_length=10,
        choices=STATUS_LEVELS,
        default="neutral",
        verbose_name="Səviyyə",
    )
    extra = models.JSONField(
        _('extra'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("order",)
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")

    def task_statuses(self, **kwargs):
        return self.filter(
            **{
                "type__model": "task",
                "type__app_label": "workspace",
            }
        ).filter(**kwargs)


class Deadline(AbstractBaseModel):
    start = models.DateTimeField()
    end = models.DateTimeField()
    account = models.ForeignKey(
        'account.Account',
        related_name='deadlines',
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(
        'workspace.Task',
        related_name='deadlines',
        on_delete=models.CASCADE,
    )
    status = models.ForeignKey(
        'workspace.Status',
        on_delete=models.DO_NOTHING,
        related_name='deadlines',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.account.get_full_name()

    class Meta:
        verbose_name = _("Deadline")
        verbose_name_plural = _("Deadlines")


class Action(AbstractBaseModel):
    user = models.ForeignKey(
        'account.Account',
        related_name='actions',
        on_delete=models.CASCADE
    )
    action_type = models.CharField(
        _('action type'),
        max_length=255,
    )
    task = models.ForeignKey(
        'workspace.Task',
        related_name='actions',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        _('time'),
        default=timezone.now
    )

    def __str__(self):
        return f'{self.user} {self.action_type} {self.task}'

    class Meta:
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")
