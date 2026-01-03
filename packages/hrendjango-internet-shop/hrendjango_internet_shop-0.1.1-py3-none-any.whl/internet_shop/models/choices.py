from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy


class AvailabilityChoices(IntegerChoices):
    NOT_AVAILABLE = 0, gettext_lazy('Not available')
    AVAILABLE = 1, gettext_lazy('Available')
    TO_ORDER = 2, gettext_lazy('To order')


class OrderStatusChoices(IntegerChoices):
    CANCELLED = 0, gettext_lazy('cancelled')
    IS_BEING_PREPARED = 1, gettext_lazy('is being prepared')
    IS_BEING_DELIVERED = 2, gettext_lazy('is being delivered')
    AWAITING = 3, gettext_lazy('awaiting')
    RECEIVED = 4, gettext_lazy('received')


class MeasureChoices(IntegerChoices):
    UNIT = 0, gettext_lazy('unit')
    KG = 1, gettext_lazy('kg')
    GRAM = 2, gettext_lazy('g')
    LITER = 3, gettext_lazy('l')
    ML = 4, gettext_lazy('ml')
    TON = 5, gettext_lazy('t')
    MG = 6, gettext_lazy('mg')
    MM = 7, gettext_lazy('mm')
    SM = 8, gettext_lazy('sm')
    METER = 9, gettext_lazy('m')
    KILOMETER = 10, gettext_lazy('km')
    