from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from workspace.models import AccountThrough, WorkSpace
from .forms import UserRegisterForm, AddInstagramForm, Add2faInstagramForm
from .models import Account, Instagram
from .tasks import check_2fa

User = get_user_model()


class AccountRegistrationView(generic.CreateView):
    """
    Account Register View
    If user is authenticated then redirect to dashboard view
    """

    template_name = "account/signup.html"
    form_class = UserRegisterForm
    model = User
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def client_list(request, ws_slug):
    workspace = WorkSpace.objects.get(slug=ws_slug)
    client_through_instances = AccountThrough.objects.filter(workspace=workspace, type=3).all()
    clients = [obj.account for obj in client_through_instances]
    context = {
        'clients': clients,
        'workspace': workspace
    }
    return render(request, 'account/client/index.html', context)


def client_detail(request, ws_slug, pk):
    workspace = WorkSpace.objects.get(slug=ws_slug)
    client = Account.objects.get(id=pk)

    context = {
        'client': client,
        'workspace': workspace
    }
    return render(request, 'account/client/detail.html', context)


def social_accounts_list(request):
    account = Account.objects.get(email=request.user.email)
    instagram = account.instagram.first()
    instagram2fa_form = Add2faInstagramForm(request.POST or None, instance=instagram)

    edit_insta_form = AddInstagramForm(request.POST or None, instance=instagram)

    if request.method == 'POST':
        add_insta_form = AddInstagramForm(request.POST or None)
        add_insta_form.instance.account = account
        if 'instagram-2fa' in request.POST:
            if instagram2fa_form.is_valid():
                instagram2fa_form.save()
                return redirect('social-accounts')
        elif 'add-instagram' in request.POST:
            if add_insta_form.is_valid():
                obj = add_insta_form.save()
                check_2fa.apply_async(args=[account.id, obj.id])
                return redirect('social-accounts')
        elif 'edit-instagram' in request.POST:
            if edit_insta_form.is_valid():
                edit_insta_form.save()
                return redirect('social-accounts')
        elif 'delete-instagram' in request.POST:
            instagram.delete()
            return redirect('social-accounts')
    else:
        add_insta_form = AddInstagramForm()

    context = {
        'instagram': account.instagram.first(),
        'instagram2fa_form': instagram2fa_form,
        'add_insta_form': add_insta_form,
        'edit_insta_form': edit_insta_form,
    }
    return render(request, 'account/social-accounts/list.html', context)


def instagram_create(request, pk):
    account = Account.objects.get(id=pk)
    form = AddInstagramForm(request.POST or None)
    form.instance.account = account
    if request.method == 'POST' and form.is_valid():
        instagram = form.save()
        check_2fa.apply_async(args=[account.id, instagram.id])
        return redirect('index')
    context = {
        'form': form
    }
    return render(request, 'account/social-accounts/instagram/create.html', context)
