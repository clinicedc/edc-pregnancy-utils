from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow


class Lmp:

    def __init__(self, lmp=None, reference_date=None):
        self.date = lmp
        self.reference_date = reference_date or get_utcnow()
        try:
            self.edd = self.date + relativedelta(days=280)
            self.ga = relativedelta(weeks=40) - relativedelta(self.edd - self.reference_date)
        except TypeError:
            self.edd = None
            self.ga = None
