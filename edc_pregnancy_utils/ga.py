from .lmp import Lmp
from .ultrasound import Ultrasound
from .constants import LMP, ULTRASOUND


class Ga:
    def __init__(self, lmp, ultrasound):
        self.ultrasound = ultrasound or Ultrasound()
        try:
            lmp = lmp.date
        except AttributeError:
            pass
        self.lmp = Lmp(lmp=lmp, reference_date=self.ultrasound.date)
        if self.lmp.ga:
            self.ga = self.lmp.ga
            self.method = LMP
        elif ultrasound.ga:
            self.ga = self.ultrasound.ga
            self.method = ULTRASOUND
        else:
            self.ga = None
            self.method = None
