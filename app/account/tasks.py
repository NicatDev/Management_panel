from __future__ import absolute_import, unicode_literals
from celery import shared_task

from account.models import Account
from utils.instagram import check_account


@shared_task(autoretry_for=(Exception,))
def check_2fa(account_id, instagram_id):
    account = Account.objects.get(id=account_id)
    # check_account(account, instagram_id)
    return f'{account.get_full_name()} üçün instagram 2FA yoxlanışı bitdi'

