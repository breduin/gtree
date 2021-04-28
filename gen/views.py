from django.views.generic import DetailView
from .models import Person, Marriage


class PersonView(DetailView):
    """
    View for details of the person
    """
    model = Person
    template_name = 'gen/person_details.html'
    context_object_name = 'person'


class MarriageView(DetailView):
    """
    View for details of the marriage
    """
    model = Marriage
    template_name = 'gen/marriage_details.html'
    context_object_name = 'marriage'
