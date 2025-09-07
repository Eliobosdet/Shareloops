from .forms import SearchForm, FilterForm

def global_forms(request):
    return {
        "searchForm": SearchForm(request.GET or None),
        "filterForm": FilterForm(request.GET or None)
    }

