from django.http import JsonResponse
from rest_framework.response import Response


class DisableCSRF(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


def response_paginated(page_obj, data, request):
    next_page = None
    previous_page = None
    request.GET.get("q", "")
    if page_obj.has_previous():
        previous_page = request.path + "?q=" + request.GET.get("q", "") + "&page=" + str(page_obj.previous_page_number())
    if page_obj.has_next():
        next_page = request.path + "?q=" + request.GET.get("q", "") + "&page=" + str(page_obj.next_page_number())
    d = {
        'next': next_page,
        'previous': previous_page,
        'count': page_obj.paginator.count,
        'results': data
    }
    return httpResponse(True, d, "Success")


def response(status, data, message):
    return Response({
        "status": status,
        "message": message,
        "data": data
    })


def httpResponse(status, data, message):
    return JsonResponse({
        "status": status,
        "message": message,
        "data": data
    }, status=200)
