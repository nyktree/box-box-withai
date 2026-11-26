from django.db.models import Count
from .models import CauseSuggestion

def get_suggestions(damage):
    return CauseSuggestion.objects.filter(category=damage.category).annotate(confirmations=Count("confirmed_damages")).order_by("-priority", "-confirmations", "cause")
