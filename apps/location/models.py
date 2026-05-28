# This file defines location-related models for the Roommate Finder app.
# It stores geographic data for Kenyan cities and areas to support location features.

from django.db import models


class KenyanArea(models.Model):
    """Pre-seeded table of Kenyan cities and areas for autocomplete and location features."""

    # City name (e.g., "Nairobi", "Mombasa")
    city = models.CharField(max_length=100)
    # Area/neighborhood within the city (e.g., "Westlands", "Kilimani")
    area = models.CharField(max_length=100)
    # Latitude coordinate for GPS mapping
    lat = models.FloatField()
    # Longitude coordinate for GPS mapping
    lng = models.FloatField()

    class Meta:
        db_table = "kenyan_areas"  # Database table name
        unique_together = [["city", "area"]]  # Ensure no duplicate city-area combinations
        ordering = ["city", "area"]  # Default ordering by city then area

    def __str__(self):
        # String representation showing area first, then city
        return f"{self.area}, {self.city}"
