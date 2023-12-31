from functools import wraps

from web_api.models_product import ZipCodes
from web_api.view import apiresponse


def zipcode_permission(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        zc = ZipCodes.objects.filter(zipcode=request.zipcode).first()
        if zc is not None:
            return function(request, *args, **kwargs)
        else:
            return apiresponse.httpResponse(False, None, "Kayi currently is not available in your area")

    return wrap
