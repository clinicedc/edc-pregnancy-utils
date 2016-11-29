from datetime import datetime

from dateutil.relativedelta import relativedelta


class Ultrasound:

    def __init__(self, ultrasound_date=None, ga_weeks=None, ga_days=None):
        self.report_date = None
        self.edd = None
        self.ga = None
        if ultrasound_date:
            self.report_date = datetime.fromordinal(ultrasound_date.toordinal())
            if ga_weeks is not None:
                if not 0 < ga_weeks < 40:
                    raise TypeError('Invalid Ultrasound GA weeks, expected 0 < ga_weeks < 40. Got {}'.format(ga_weeks))
            ga_days = ga_days or 0
            if not 0 <= ga_days <= 6:
                raise TypeError('Invalid Ultrasound GA days, expected 0 <= ga_days <= 6. Got {}'.format(ga_days))
            try:
                self.ga = relativedelta(weeks=ga_weeks) + relativedelta(days=ga_days)
            except TypeError:
                pass
            if self.ga:
                self.edd = self.report_date + self.ga
