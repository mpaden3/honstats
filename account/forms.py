from django import forms


class SearchForm(forms.Form):
    search_term = forms.CharField(
        label="Search nickname or Match ID", max_length=100, required=True
    )

    def is_match_id(self):
        search_term = self.cleaned_data["search_term"]
        return search_term.isnumeric()

    def get_search_term(self):
        return self.cleaned_data["search_term"]
