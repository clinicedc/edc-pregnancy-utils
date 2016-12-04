from .constants import LMP, ULTRASOUND
from .lmp import Lmp
from .ultrasound import Ultrasound


class Ga:
    def __init__(self, lmp, ultrasound, prefer_ultrasound=True):
        """Returns a delta of the GA.

        by default, if both Lmp and Ultrasound are provided, Ultrasound is used."""
        self.ultrasound = ultrasound or Ultrasound()
        try:
            if prefer_ultrasound:
                self.lmp = Lmp(lmp=lmp.date, reference_date=self.ultrasound.ultrasound_date or lmp.reference_date)
            else:
                self.lmp = Lmp(lmp=lmp.date, reference_date=lmp.reference_date or self.ultrasound.ultrasound_date)
        except AttributeError:
            self.lmp = Lmp()
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
        try:
            weeks = self.ga.weeks
        except AttributeError:
            weeks = None
        return weeks
