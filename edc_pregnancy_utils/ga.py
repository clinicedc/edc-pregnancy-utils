from datetime import datetime

from edc_base.utils import get_utcnow

from .lmp import Lmp
from .ultrasound import Ultrasound
from .constants import LMP, ULTRASOUND


class Ga:
    def __init__(self, lmp, ultrasound, prefer_ultrasound=True):
        """Returns a delta of the GA.

        by default, if both Lmp and Ultrasound are provided, Ultrasound is used."""
        self.ultrasound = ultrasound or Ultrasound()
        try:
            lmp = datetime.fromordinal(lmp.toordinal())
        except AttributeError:
            lmp = lmp.date
        self.lmp = Lmp(lmp=lmp, reference_date=self.ultrasound.date or get_utcnow())
        self.ga = None
        self.method = None
        if prefer_ultrasound:
            if ultrasound.ga:
                self.ga, self.method = self.ultrasound.ga, ULTRASOUND
            elif self.lmp.ga:
                self.ga, self.method = self.lmp.ga, LMP
        else:
            if self.lmp.ga:
                self.ga, self.method = self.lmp.ga, LMP
            elif ultrasound.ga:
                self.ga, self.method = self.ultrasound.ga, ULTRASOUND

    @property
    def weeks(self):
        return self.ga.weeks
