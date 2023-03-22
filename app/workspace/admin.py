from django.contrib import admin
from .models import WorkSpace, AccountThrough, Task, TaskFile, Status, Deadline, Action


class InlineAccountThroughAdmin(admin.TabularInline):
    model = AccountThrough
    extra = 1


@admin.register(WorkSpace)
class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ['slug']
    inlines = (InlineAccountThroughAdmin,)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'workspace']
    readonly_fields = ['slug']


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    list_display = ['task']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'next_step', 'order']


@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ['account', 'start', 'end']


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'task', 'timestamp']
