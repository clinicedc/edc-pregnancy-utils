from datetime import datetime
from dateutil.relativedelta import relativedelta


class Lmp:

    def __init__(self, lmp=None, reference_date=None):
        """Calulcates EDD and GA based on an LMP and a reference date."""
        self.edd = None
        self.ga = None
        self.date = None
        self.diffdays = None
        self.diffweeks = None
        self.reference_date = None
        if lmp:
            lmp = datetime.fromordinal(lmp.toordinal())
            reference_date = datetime.fromordinal(reference_date.toordinal())
            self.edd = lmp + relativedelta(days=280)
            self.diffdays = abs(self.edd - reference_date).days
            self.diffweeks = self.diffdays / 7.0
            self.ga = relativedelta(weeks=int(40 - self.diffweeks))
            self.date = lmp
            self.reference_date = reference_date
            try:
                self.edd = self.edd.date()
            except AttributeError:
                pass
            try:
                self.date = self.date.date()
            except AttributeError:
                pass
