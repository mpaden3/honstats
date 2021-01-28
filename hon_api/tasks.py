import subprocess

from hon_api.models import ApiKey


def api_login():
    result = subprocess.run(
        ["./refresh_api_login.sh"], stdout=subprocess.PIPE, shell=True
    )

    cookie = result.stdout.decode().replace("\n", "")

    api_key = ApiKey.objects.all().first()
    api_key.cookie = cookie
    api_key.save()

    return cookie
