from dateutil.relativedelta import relativedelta

from .constants import ULTRASOUND, LMP
from .lmp import Lmp
from .ultrasound import Ultrasound


class Edd:

    def __init__(self, lmp=None, ultrasound=None):
        self.edd = None
        self.method = None
        self.lmp = lmp or Lmp()
        self.ultrasound = ultrasound or Ultrasound()
        self.method = None
        try:
            self.edd = self.get_edd(relativedelta(days=abs(relativedelta(self.lmp.edd - self.ultrasound.date).days)))
        except TypeError as e:
            if self.lmp.edd:
                self.edd = self.lmp.edd
                self.method = LMP
            elif self.ultrasound.edd:
                self.edd = self.ultrasound.edd
                self.method = ULTRASOUND
            elif not self.lmp.edd and not self.ultrasound.edd:
                pass
            else:
                raise TypeError(str(e))

    def get_edd(self, delta):
        edd = None
        if relativedelta(weeks=16) <= self.lmp.ga <= relativedelta(weeks=21) + relativedelta(days=6):
            if 0 <= delta.days <= 10:
                edd = self.lmp.edd
                self.method = LMP
            elif 10 < delta.days:
                edd = self.ultrasound.edd
                self.method = ULTRASOUND
        elif (relativedelta(weeks=21) + relativedelta(days=6) < self.lmp.ga <=
              relativedelta(weeks=27) + relativedelta(days=6)):
            if 0 <= delta.days <= 14:
                edd = self.lmp.edd
                self.method = LMP
            elif 14 < delta.days:
                edd = self.ultrasound.edd
                self.method = ULTRASOUND
        elif relativedelta(weeks=27) + relativedelta(days=6) < self.lmp.ga:
            if 0 <= delta.days <= 21:
                edd = self.lmp.edd
                self.method = LMP
            elif 21 < delta.days:
                edd = self.ultrasound.edd
                self.method = ULTRASOUND
        return edd
