from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.utils import timezone
# from django.forms.models import modelformset_factory
from django.forms import modelformset_factory
from account.models import Account
from .forms import WorkSpaceForm, ClientMemberAddForm, TaskCreateForm, DeadlineForm, TaskUpdateForm

from workspace.models import WorkSpace, AccountThrough, Task, Deadline, TaskFile, Action


class WorkSpaceCreateView(LoginRequiredMixin, CreateView):
    model = WorkSpace
    template_name = 'workspace/create.html'
    form_class = WorkSpaceForm

    def form_valid(self, form):
        workspace = WorkSpace.objects.create(title=form.cleaned_data.get('title'))
        account = Account.objects.get(email=self.request.user.email)
        instance = AccountThrough.objects.create(workspace=workspace, account=account)
        instance.save()
        return redirect(reverse('workspaces'))


class WorkSpaceListView(LoginRequiredMixin, ListView):
    model = WorkSpace
    template_name = 'workspace/list.html'

    def get_context_data(self, **kwargs):
        context = super(WorkSpaceListView, self).get_context_data(**kwargs)
        context['your_workspaces'] = WorkSpace.objects.filter(
            accounts__account=self.request.user,
            accounts__type=1,
        )
        context['guest_workspaces'] = WorkSpace.objects.filter(
            accounts__account=self.request.user,
            accounts__type=2,
        )
        return context


# =================== WorkSpace detail and client create for WorkSpace ===========================
class WorkSpaceDetailView(LoginRequiredMixin, DetailView):
    model = WorkSpace
    template_name = 'workspace/ws-detail.html'
    context_object_name = 'workspace'

    def get_context_data(self, **kwargs):
        context = super(WorkSpaceDetailView, self).get_context_data(**kwargs)
        context['clients'] = Account.objects.filter(
            workspace__workspace=self.object,
            workspace__type=3,
        )
        context['form'] = ClientMemberAddForm
        return context

    def get_object(self, queryset=None):
        return WorkSpace.objects.get(slug=self.kwargs.get('ws_slug'))


class ClientMemberAddView(LoginRequiredMixin, CreateView):
    model = AccountThrough
    template_name = 'workspace/ws-detail.html'
    form_class = ClientMemberAddForm

    def form_valid(self, form):
        form.instance.workspace = WorkSpace.objects.get(slug=self.kwargs.get('ws_slug'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workspace-detail', kwargs={'ws_slug': self.kwargs.get('ws_slug')})


# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
@login_required
def ws_list(request):
    all_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
        accounts__type__in=[1, 2],
    )
    my_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
        accounts__type=1,
    )
    joined_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
        accounts__type=2,
    )

    if request.method == 'POST':
        ws_form = WorkSpaceForm(request.POST or None)
        if ws_form.is_valid():
            workspace = WorkSpace.objects.create(title=ws_form.cleaned_data.get('title'))
            account = Account.objects.get(email=request.user.email)
            instance = AccountThrough.objects.create(workspace=workspace, account=account)
            instance.save()
            return redirect('workspaces')
    else:
        ws_form = WorkSpaceForm()

    context = {
        'all_workspaces': all_ws,
        'my_workspaces': my_ws,
        'joined_workspaces': joined_ws,
        'ws_form': ws_form
    }
    return render(request, 'workspace/list.html', context)


@login_required
def ws_detail(request, ws_slug):
    """
    combine client detail and task create views in one view
    """
    ws = WorkSpace.objects.get(slug=ws_slug)
    form = TaskCreateForm(request.POST or None, wk_id=ws.id)
    form.instance.workspace = WorkSpace.objects.get(slug=ws_slug)
    deadline_formset = modelformset_factory(Deadline, form=DeadlineForm, extra=0)
    formset = deadline_formset(request.POST or None, queryset=Deadline.objects.none(), form_kwargs={'wk_id': ws.id})

    accounts = [acc.id for acc in AccountThrough.objects.filter(workspace=ws.id, type=2)]
    members = Account.objects.filter(workspace__in=accounts)

    ws_tasks_ids = [task.id for task in ws.tasks.all()]
    actions = Action.objects.filter(task__in=ws_tasks_ids).order_by('-timestamp')

    context = {
        'form': form,
        'formset': formset,
        'workspace': ws,
        'ws_slug': ws.slug,
        'ws_members': members,
        'actions': actions,
    }

    if all([form.is_valid(), formset.is_valid()]):
        obj = form.save(commit=False)
        obj.save()
        Action.objects.create(user=request.user, action_type='created', task=obj)
        for form2 in formset:
            child = form2.save(commit=False)
            child.task = obj
            child.save()
        return redirect('workspace-detail', ws_slug=ws_slug)
    return render(request, 'workspace/ws-detail.html', context)


@login_required
def ws_update(request, pk):
    workspace = get_object_or_404(WorkSpace, id=pk)
    if request.method == 'POST':
        ws_form = WorkSpaceForm(request.POST or None, instance=workspace)
        if ws_form.is_valid():
            ws_form.save()
            return redirect('workspaces')
    else:
        ws_form = WorkSpaceForm(instance=workspace)

    all_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
    )
    my_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
        accounts__type=1,
    )
    joined_ws = WorkSpace.objects.filter(
        accounts__account=request.user,
        accounts__type=2,
    )

    context = {
        'all_workspaces': all_ws,
        'my_workspaces': my_ws,
        'joined_workspaces': joined_ws,
        'ws_edit_form': ws_form
    }
    return render(request, 'workspace/list.html', context)


@login_required
def delete_workspace(request, pk):
    workspace = get_object_or_404(WorkSpace, id=pk)

    # check if the logged-in user has permission to delete the workspace
    if workspace.accounts.filter(account=request.user, type=1).exists():
        workspace.delete()
        # messages.success(request, 'Workspace deleted successfully.')
    else:
        # messages.error(request, 'You do not have permission to delete this workspace.')
        return redirect('workspaces')
    return redirect('workspaces')


@login_required
def remove_ws_member(request, ws_slug, pk):
    workspace = get_object_or_404(WorkSpace, slug=ws_slug)
    member = get_object_or_404(Account, id=pk)
    # check if the logged-in user has permission to delete the workspace
    if workspace.accounts.filter(account=request.user, type=1).exists():
        account_through = AccountThrough.objects.filter(workspace=workspace, account=member).first()
        account_through.delete()
        # messages.success(request, 'Workspace deleted successfully.')
    else:
        # messages.error(request, 'You do not have permission to delete this workspace.')
        return redirect('workspace-detail', ws_slug=ws_slug)
    return redirect('workspace-detail', ws_slug=ws_slug)


@login_required
def search_account(request, ws_slug):
    search_text = request.POST.get('user-add-search')
    print(search_text)
    results = Account.objects.filter(email=search_text)
    print(results)
    workspace = WorkSpace.objects.get(slug=ws_slug)
    context = {"results": results,
               'workspace': workspace,
    }
    return render(request, 'partials/search-results.html', context)


@login_required
def add_member_to_ws(request, ws_slug):
    email = request.POST.get('email')
    type = request.POST.get('type')
    print('type-a geeeeel ========================', type)
    workspace = WorkSpace.objects.get(slug=ws_slug)
    if account:= Account.objects.get(email=email):
        AccountThrough.objects.get_or_create(account=account, workspace=workspace, type=type)
    return render(request, 'partials/member_list.html', {'workspace': workspace})


# def task_detail(request, ws_slug, task_slug):
#     ws = get_object_or_404(WorkSpace, slug=ws_slug)
#     task = get_object_or_404(Task, slug=task_slug)
#
#     DeadlineFormSet = modelformset_factory(Deadline, form=DeadlineForm, extra=0)
#     form = TaskCreateForm(instance=task, wk_id=ws.id)
#     form.instance.workspace = ws
#     formset = DeadlineFormSet(queryset=Deadline.objects.filter(task=task), form_kwargs={'wk_id': ws.id})
#
#     if request.method == 'POST':
#         if 'update-status' in request.POST:
#             if task.status.next_step:
#                 task.status = task.status.next_step
#                 task.save()
#             return redirect('task-detail', ws_slug=ws_slug, task_slug=task_slug)
#         else:
#             form = TaskCreateForm(request.POST or None, instance=task, wk_id=ws.id)
#             form.instance.workspace = ws
#             formset = DeadlineFormSet(request.POST or None, queryset=Deadline.objects.filter(task=task),
#                                       form_kwargs={'wk_id': ws.id})
#             print('Posta girir ======================================================================')
#             if form.is_valid() and formset.is_valid():
#                 print('Valid-e girir ======================================================================')
#                 form.save(commit=False)
#                 for form2 in formset:
#                     child = form2.save(commit=False)
#                     child.task = task
#                     child.save()
#                 print('okeydiiiiiiiiiiiiiiiiiiiiiii')
#                 return redirect('task-detail', ws_slug=ws_slug, task_slug=task_slug)
#             else:
#                 print('valid-e girmedi')
#                 return redirect('task-detail', ws_slug=ws_slug, task_slug=task_slug)
#
#     context = {
#         'workspace': ws,
#         'task': task,
#         'form': form,
#         'formset': formset,
#     }
#     return render(request, 'workspace/task/detail.html', context)

@login_required
def task_detail(request, ws_slug, task_slug):
    ws = get_object_or_404(WorkSpace, slug=ws_slug)
    task = get_object_or_404(Task, slug=task_slug, workspace=ws)
    actions = task.actions.all().order_by('-timestamp')

    # DeadlineFormSet = modelformset_factory(
    #     Deadline, form=DeadlineForm, extra=0, can_delete=True, can_delete_extra=True
    # )
    form = TaskUpdateForm(instance=task, wk_id=ws.id)
    # formset = DeadlineFormSet(
    #     request.POST or None,
    #     queryset=task.deadlines.all(),
    #     form_kwargs={'wk_id': ws.id},
    # )

    if request.method == 'POST':
        if 'update-status' in request.POST:
            if task.status.next_step:
                task.status = task.status.next_step
                task.save()
                Action.objects.create(user=request.user, action_type='changed status of', task=task)
            return redirect('task-detail', ws_slug=ws_slug, task_slug=task_slug)
        else:
            form = TaskUpdateForm(request.POST or None, request.FILES, instance=task, wk_id=ws.id)
            if form.is_valid():
                files = request.FILES.getlist('file')
                obj = form.save()
                Action.objects.create(user=request.user, action_type='updated', task=task)
                for file in files:
                    TaskFile.objects.create(task=obj, file=file)
                # for form2 in formset:  # Set the task instance for new forms
                #     child = form2.save(commit=False)
                #     child.task = obj
                #     child.save()
                return redirect('task-detail', ws_slug=ws_slug, task_slug=task_slug)

    context = {
        'workspace': ws,
        'task': task,
        'form': form,
        'actions': actions,
    }
    return render(request, 'workspace/task/detail.html', context)
