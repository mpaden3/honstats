from django.urls import reverse
from django.views.generic import FormView, ListView

from account.forms import SearchForm
from blog.models import BlogPost
from match.models import Match


class BlogListView(ListView):
    model = BlogPost
    queryset = BlogPost.objects.order_by("-created")


class HomepageView(FormView):
    template_name = "homepage.html"
    form_class = SearchForm
    success_url = None

    def form_valid(self, form):

        if form.is_match_id():
            self.success_url = reverse("match-detail", args=[form.get_search_term()])
            return super().form_valid(form)

        self.success_url = f"{reverse('account-search')}?s={form.get_search_term()}"
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matches"] = Match.objects.exclude(parsed_level=Match.KNOWN).order_by(
            "-match_date"
        )[:30]
        context["blog_posts"] = BlogPost.objects.order_by("-created").all()[:3]
        return context
