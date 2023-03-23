from django import forms
from django.contrib.contenttypes.models import ContentType
from account.models import Account
from .models import WorkSpace, AccountThrough, Task, Deadline, Status, TaskFile
from django.utils.translation import gettext_lazy as _
from utils.options import ACCOUNT_CHOICES, SHARING_TYPES
from ckeditor.widgets import CKEditorWidget


class WorkSpaceForm(forms.ModelForm):
    title = forms.CharField()

    class Meta:
        model = WorkSpace
        fields = ['title']


class ClientMemberAddForm(forms.ModelForm):
    # account = forms.ModelChoiceField(queryset=Account.objects.all(),
    #                                  empty_label="",
    #                                  widget=forms.Select(attrs={'class': 'form-select'}))
    # account.empty_label = 'Select'
    type = forms.ChoiceField(choices=ACCOUNT_CHOICES,
                             widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = AccountThrough
        fields = ['type', 'account']


class TaskCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        wk_id = kwargs.pop("wk_id")
        accounts = [acc.id for acc in AccountThrough.objects.filter(workspace=wk_id, type=3)]
        super().__init__(*args, **kwargs)
        self.fields["client"] = forms.ModelChoiceField(queryset=Account.objects.filter(workspace__in=accounts),
                                     empty_label="Select client",
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    title = forms.CharField()
    description = forms.CharField()
    deadline = forms.DateTimeField()
    sharing_type = forms.ChoiceField(choices=SHARING_TYPES,
                                     widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Task
        fields = ['client', 'title', 'description', 'sharing_type', 'deadline']


class DeadlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        wk_id = kwargs.pop("wk_id")
        accounts = [acc.id for acc in AccountThrough.objects.filter(workspace=wk_id, type=2)]
        super().__init__(*args, **kwargs)
        self.fields["account"] = forms.ModelChoiceField(queryset=Account.objects.filter(workspace__in=accounts),
                                     empty_label="Assign member",
                                     widget=forms.Select(attrs={'class': 'form-select mb-3 mt-2'}))
    # account.empty_label = 'Assign member'
    start = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'class': 'form-control mb-3 mt-2',
                                                                                 'type': 'datetime-local'}))
    end = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'class': 'form-control mb-3 mt-2',
                                                                                 'type': 'datetime-local'}))
    # task_type = ContentType.objects.get(model='task')
    status = forms.ModelChoiceField(queryset=Status.objects.all(),
                                    empty_label="Select status",
                                    widget=forms.Select(attrs={'class': 'form-select mb-3 mt-2'}))
    class Meta:
        model = Deadline
        fields = ['account', 'start', 'end', 'status']


class TaskUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        wk_id = kwargs.pop("wk_id")
        accounts = [acc.id for acc in AccountThrough.objects.filter(workspace=wk_id, type=3)]
        super().__init__(*args, **kwargs)
        self.fields["client"] = forms.ModelChoiceField(queryset=Account.objects.filter(workspace__in=accounts),
                                     empty_label="Select client",
                                     widget=forms.Select(attrs={'class': 'form-select'}))

    files = forms.ModelMultipleChoiceField(
        queryset=TaskFile.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    title = forms.CharField()
    description = forms.CharField()
    deadline = forms.DateTimeField()
    sharing_type = forms.ChoiceField(choices=SHARING_TYPES,
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Task
        fields = ['client', 'title', 'description', 'text', 'file', 'sharing_platform', 'sharing_type', 'deadline']
