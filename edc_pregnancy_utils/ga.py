from .lmp import Lmp
from .ultrasound import Ultrasound


class Ga:
    def __init__(self, lmp, ultrasound):
        self.ultrasound = ultrasound or Ultrasound()
        try:
            lmp = lmp.date
        except AttributeError:
            pass
        self.lmp = Lmp(lmp=lmp, reference_date=self.ultrasound.date)
        self.ga = self.lmp.ga or ultrasound.ga
