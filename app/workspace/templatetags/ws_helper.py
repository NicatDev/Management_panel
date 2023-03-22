import os

from django import template

register = template.Library()

@register.filter
def members(workspace):
    res = workspace.accounts.all()
    return [account.account for account in res]


@register.filter
def members_count(workspace):
    res = workspace.accounts.filter(type=2)
    return len([account.account for account in res])


@register.filter
def clients_count(workspace):
    res = workspace.accounts.filter(type=3)
    return len([account.account for account in res])


@register.filter
def client_workspaces(client):
    res = client.workspace.filter(type=3)
    return [obj.workspace for obj in res]


@register.filter
def get_first_letters(full_name):
    res = [word[0] for word in full_name.split()]
    return ''.join(res)


@register.filter
def filename(value):
    return os.path.basename(value.file.name)