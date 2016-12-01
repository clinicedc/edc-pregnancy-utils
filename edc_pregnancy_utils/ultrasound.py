from datetime import datetime

from dateutil.relativedelta import relativedelta


class UltrasoundError(Exception):
    pass


class Ultrasound:

    def __init__(self, ultrasound_date=None, ga_confirmed_weeks=None, ga_confirmed_days=None, ultrasound_edd=None):
        self.ultrasound_date = None
        self.edd = None
        self.ga = None
        if ultrasound_date and ultrasound_edd and ga_confirmed_weeks is not None:
            self.ultrasound_date = datetime.fromordinal(ultrasound_date.toordinal())
            ultrasound_edd = datetime.fromordinal(ultrasound_edd.toordinal())
            if not 0 < ga_confirmed_weeks < 40:
                raise UltrasoundError(
                    'Invalid Ultrasound GA weeks, expected 0 < ga_weeks < 40. Got {}'.format(ga_confirmed_weeks))
            ga_confirmed_days = ga_confirmed_days or 0
            if not 0 <= ga_confirmed_days <= 6:
                raise UltrasoundError(
                    'Invalid Ultrasound GA days, expected 0 <= ga_days <= 6. Got {}'.format(ga_confirmed_days))
            tdelta = ultrasound_edd - self.ultrasound_date
            calculated_ga = relativedelta(weeks=40) - relativedelta(days=tdelta.days)
            ultrasound_ga = relativedelta(weeks=ga_confirmed_weeks) + relativedelta(days=ga_confirmed_days)
            if ultrasound_ga.weeks == calculated_ga.weeks:
                self.ga = calculated_ga
            else:
                raise UltrasoundError(
                    'Ultrasound GA confirmed and GA calculated do not match. '
                    'Got {} != {} using weeks={}, days={}.'.format(
                        ultrasound_ga, calculated_ga, ga_confirmed_weeks, ga_confirmed_days))
            self.ga = ultrasound_ga
            calculated_edd = self.ultrasound_date + (relativedelta(weeks=40) - self.ga)
            if abs(ultrasound_edd - calculated_edd).days <= 6:
                self.edd = ultrasound_edd
            else:
                raise UltrasoundError(
                    'Ultrasound EDD and calculated EDD do not match. Got {} != {}.'.format(
                        ultrasound_edd.isoformat(), self.edd.isoformat()))
