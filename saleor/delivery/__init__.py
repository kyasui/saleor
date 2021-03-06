from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from prices import Price
from satchless.item import ItemSet


class BaseDelivery(ItemSet):

    group = None
    name = ''

    def __init__(self, delivery_group):
        self.group = delivery_group

    def __iter__(self):
        return iter(self.group)

    def get_delivery_total(self, **kwargs):
        return Price(0, currency=settings.DEFAULT_CURRENCY)

    def get_total_with_delivery(self):
        return self.group.get_total() + self.get_delivery_total()


@python_2_unicode_compatible
class DummyShipping(BaseDelivery):
    name = 'dummy_shipping'

    def __init__(self, delivery_group, address):
        self.address = address
        super(DummyShipping, self).__init__(delivery_group)

    def __str__(self):
        return 'Dummy shipping'

    def get_delivery_total(self, weight=None, **kwargs):
        if weight is None:
            weight = sum(line.product.get_weight() for line in self.group)
        qty = sum(line.quantity for line in self.group)
        return Price(qty * weight,
                     currency=settings.DEFAULT_CURRENCY)


def get_delivery_choices_for_group(group, **kwargs):
    if 'address' in kwargs:
        shipping = DummyShipping(group, kwargs['address'])
        yield (shipping.name, shipping)
    else:
        raise ValueError('Unknown delivery type')


def get_delivery(group):
    if group.method == 'dummy_shipping':
        return DummyShipping(group, group.shippeddeliverygroup.address)
    else:
        raise ValueError('Unknown delivery method')
