# This file contains utility functions used across the Roommate Finder app.
# These are shared helper functions for common operations like distance calculation and API responses.

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lng points using Haversine formula."""
    # Earth's radius in kilometers
    R = 6371
    # Convert latitudes to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    # Calculate differences in coordinates and convert to radians
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    # Haversine formula calculation
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    # Return distance using atan2 for numerical stability
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def success_response(data=None, message='Success', status=200):
    """Create a standardized success response for API endpoints."""
    return {'status': 'success', 'message': message, 'data': data}


def error_response(message='Error', errors=None):
    """Create a standardized error response for API endpoints."""
    return {'status': 'error', 'message': message, 'errors': errors}
