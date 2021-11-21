import random
import time

from account.models import Account
from account.tasks import fetch_account_data


def fix_mmr():
    accounts = Account.objects.all()

    for account in accounts:
        if account.current_mmr is None:
            fetch_account_data(account.nickname)
            print(f"Fetched {account.nickname}")
            r = random.randint(1, 10)
            time.sleep(r)
