from django.http import Http404

from hon_api.tasks import get_match_stats
from match.utils import update_or_create_match_full


def fetch_match_data(match_id):
    data = get_match_stats(match_id)

    if "date" not in data["match_summ"][match_id]:
        raise Http404

    return update_or_create_match_full(match_id, data)
