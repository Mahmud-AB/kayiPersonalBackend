import json

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from web_api.models import AuditLog
from web_api.view import apiresponse
from web_view.view.httpresponse import template


class AdminSellerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        req_path = str(request.path)
        web_auth_path = ['/service', '/seller']
        api_auth_path = ['/api/product/card', '/api/product/whitelist', '/api/product/order']
        try:
            if len(request.META.get("HTTP_ZIPCODE", "0")) > 0:
                request.zipcode = int(request.META.get("HTTP_ZIPCODE", "0"))

            if hasattr(request, "user") is False:
                return response_api_html(request)
            # print("email" + str(request.user.email) + " zipcode: " + str(request.zipcode))

            if req_path.startswith(web_auth_path[0]) and not request.user.is_superuser:
                return redirect('/login/')
            elif req_path.startswith(web_auth_path[1]) and not request.user.is_staff:
                return redirect('/login/')

            for wap in api_auth_path:
                if req_path.startswith(wap):
                    if request.user.is_anonymous:
                        return apiresponse.httpResponse(False, None, "Please sign in")

        except Exception as ex:
            print(str(ex))
            return response_api_html(request)

    def process_response(self, request, response):
        return response


def response_api_html(request):
    ct = str(request.content_type)
    if ct.find("text") or ct.find("html"):
        return template(request, "505.html", {'message': "Please contact the support team"})
    else:
        return apiresponse.httpResponse(False, None, "Please contact the support team")


class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        try:
            content = str(response._content_type_for_repr)
            if response.status_code != 404 and request.method == 'POST':
                audit = AuditLog()
                audit.user = request.user
                audit.status = response.status_code
                audit.method = request.method
                audit.path = request.path
                if len(request.POST) > 0:
                    audit.request_param = json.dumps(request.POST)
                else:
                    audit.request_param = json.dumps(request.GET)
                if request.body is not None:
                    audit.request_payload = request.body.decode('utf-8')
                if content.find('json') >= 0:
                    audit.response = response.content.decode('utf-8')
                audit.save()
            if content.find('json') >= 0:
                print("------------------------------------------------------------------------------------------")
                # print(response.content.decode('utf-8'))
        except Exception as ex:
            print(str(ex))
        return response
