from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import rrule


class Lmp:

    def __init__(self, lmp=None, reference_date=None):
        """Calulcates EDD and GA based on an LMP and a reference date."""
        self.edd = None
        self.ga = None
        self.date = None
        self.reference_date = None
        if lmp:
            lmp = datetime.fromordinal(lmp.toordinal())
            reference_date = datetime.fromordinal(reference_date.toordinal())
            self.edd = lmp + relativedelta(days=280)
            weeks = rrule.rrule(rrule.WEEKLY, dtstart=lmp, until=reference_date)
            weeks = len([dt for dt in list(weeks) if dt != lmp])
            self.ga = relativedelta(weeks=40) - relativedelta(weeks=weeks)
            self.date = lmp
            self.reference_date = reference_date
