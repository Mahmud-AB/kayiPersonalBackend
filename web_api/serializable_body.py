import json
from json import JSONEncoder


class BodyOrder(JSONEncoder):
    def __init__(self, product, quantity, other):
        self.product = int(product)
        self.product_quantity = int(quantity)
        self.other = str(other)


class BodyPaypalPayment:
    def __init__(self, data):
        self.payer_id = data.get('payer_id', '')
        self.paypal_sdk_id = data.get('paypal_sdk_id', '')
        self.json = data


class BodyPayment:
    def __init__(self, request):
        data = json.loads(request.body.decode("utf-8"))
        self.payment_type = data.get('type', '')
        self.order_id = int(data.get('order_id', '0'))
        self.pick_up_address = data.get('pick_up_address')
        if data.get('payment_info') is not None:
            self.payment_info = BodyPaypalPayment(data.get('payment_info'))
