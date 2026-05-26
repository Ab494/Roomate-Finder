import django_filters

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    min_rent = django_filters.NumberFilter(field_name="rent", lookup_expr="gte")
    max_rent = django_filters.NumberFilter(field_name="rent", lookup_expr="lte")
    city = django_filters.CharFilter(lookup_expr="icontains")
    area = django_filters.CharFilter(lookup_expr="icontains")
    furnished = django_filters.ChoiceFilter(choices=Listing.FURNISHED_CHOICES)
    preferred_gender = django_filters.CharFilter()
    smoking_allowed = django_filters.BooleanFilter()
    pets_allowed = django_filters.BooleanFilter()
    has_wifi = django_filters.BooleanFilter()
    has_parking = django_filters.BooleanFilter()

    class Meta:
        model = Listing
        fields = [
            "min_rent",
            "max_rent",
            "city",
            "area",
            "furnished",
            "preferred_gender",
            "smoking_allowed",
            "pets_allowed",
            "has_wifi",
            "has_parking",
            "status",
        ]
