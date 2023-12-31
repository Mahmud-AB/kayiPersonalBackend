from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from config import settings
from config.settings import EMAIL_HOST_USER


def email_support_message(request):
    context = {
        'full_text': request.POST.get("message"),
        'user_name': str(request.POST.get("first_name", "")) + " " + str(request.POST.get("last_name")),
        'user_email ': request.POST.get("email", ""),
        'user_phone ': request.POST.get("mobile_no", ""),
        'request': request
    }
    html_message = render_to_string('email_template_support.html', context)
    mail.send_mail((str(request.POST.get("subject", "")) + ""), strip_tags(html_message), ('TheKayi <' + EMAIL_HOST_USER + '>'), [settings.EMAIL_HOST_USER_SUPPORT], html_message=html_message)
    print("Email password change")


def email_password_change(request, user, code):
    if code is not None:
        context = {
            'app_gen_code': code,
            'name': user.get_full_name(),
            'request': request
        }
        html_message = render_to_string('email_template_fp.html', context)
        mail.send_mail('TheKayi reset password', strip_tags(html_message), ('TheKayi <' + EMAIL_HOST_USER + '>'), [user.email], html_message=html_message)
        print("Email password change")


def email_change_email(request, user, previous_email):
    print("Email email change")


def email_order_shipped(request, order):
    context = {
        'name': order.user.get_full_name(),
        'request': request,
        'order': order
    }
    html_message = render_to_string('email_template_shipping.html', context)
    mail.send_mail('TheKayi || Ready to Ship #' + str(order.id), strip_tags(html_message), ('TheKayi <' + EMAIL_HOST_USER + '>'), [order.user.email], html_message=html_message)
    print("Ready to Ship")
