import unittest

from datetime import datetime

from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from .constants import ULTRASOUND, LMP
from .edd import Edd
from .ga import Ga
from .lmp import Lmp
from .ultrasound import Ultrasound


class TestPregnancyUtils(unittest.TestCase):

    def test_lmp_none(self):
        """Assert Lmp handles None."""
        lmp = Lmp()
        self.assertIsNone(lmp.edd)

    def test_lmp_edd(self):
        """Assert Lmp return edd."""
        dt = get_utcnow()
        edd = datetime.fromordinal((dt + relativedelta(days=280)).toordinal())
        self.assertEqual(edd, Lmp(lmp=dt, reference_date=get_utcnow()).edd)

    def test_lmp_ga(self):
        """Assert Lmp return edd."""
        dt = get_utcnow().date()
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt)
        self.assertEqual(lmp.ga.weeks, 15)

    def test_ultrasound_days_boundaries(self):
        """Assert Ultrasound raises errors for invalid days."""
        dt = get_utcnow()
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=1, ga_days=7)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=1, ga_days=-1)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

    def test_ultrasound_weeks_boundaries(self):
        """Assert Ultrasound raises errors for invalid weeks."""
        dt = get_utcnow()
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=-1)
            self.fail('TypeError not raised!')
        except TypeError:
            pass
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=0)
            self.fail('TypeError not raised!')
        except TypeError:
            pass
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=40)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

    def test_ultrasound_weeks_floor(self):
        """Assert ga weeks is rounded down to nearest int."""
        dt = get_utcnow()
        for week in range(1, 40):
            for day in range(0, 7):
                ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=week, ga_days=day)
                self.assertEqual(week, ultrasound.ga.weeks)

    def test_ultrasound_ga(self):
        """Assert Ultrasound returns ga in weeks, as is."""
        dt = get_utcnow()
        ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=25, ga_days=3)
        self.assertEqual(ultrasound.ga.weeks, 25)

    def test_ultrasound_edd(self):
        """Assert Ultrasound returns edd as future date."""
        dt = get_utcnow()
        for week in range(1, 40):
            for day in range(0, 7):
                ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=week, ga_days=day)
                self.assertGreater(ultrasound.edd.date(), dt.date())

    def test_edd_none(self):
        """Assert Edd can handle nulls."""
        lmp = Lmp()
        ultrasound = Ultrasound()
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertIsNone(edd.edd)
        edd = Edd(lmp=None, ultrasound=None)
        self.assertIsNone(edd.edd)
        edd = Edd()
        self.assertIsNone(edd.edd)

    def test_ultrasound_none(self):
        """Assert Ultrasound can handle nulls."""
        ultrasound = Ultrasound()
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)
        ultrasound = Ultrasound(None, 25, 3)
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)

    def test_edd_without_ultrasound(self):
        """Assert Edd chooses Lmp.edd if Utrasound is null."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - (relativedelta(weeks=25) + relativedelta(days=3)), reference_date=get_utcnow())
        ultrasound = Ultrasound(None, 25, 3)
        edd = Edd(lmp, ultrasound)
        self.assertEqual(edd.edd, lmp.edd)
        self.assertEqual(edd.method, LMP)

    def test_edd_without_lmp(self):
        """Assert Edd chooses Ultrasound.edd if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        edd = Edd(lmp, ultrasound)
        self.assertEqual(edd.edd, ultrasound.edd)
        self.assertEqual(edd.method, ULTRASOUND)

    def test_ga_without_lmp_uses_ultrasound(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.ga, ultrasound.ga)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_without_ultrasound_uses_lmp(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - (relativedelta(weeks=25) + relativedelta(days=3)), reference_date=get_utcnow())
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, lmp.ga.weeks)
        self.assertEqual(ga.method, LMP)

    def test_ga_without_lmp_without_ultrasound_is_none(self):
        """Assert Ga null of no lmp and no ultrasound."""
        lmp = Lmp()
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.ga, None)
        self.assertEqual(ga.method, None)

    def test_ga_weeks_from_lmp(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        dt = get_utcnow()
        lmp = dt - (relativedelta(weeks=25) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp, reference_date=dt)
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 15)
        self.assertEqual(ga.method, LMP)

    def test_ga_weeks_from_ultrasound(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_weeks_from_ultrasound_if_both(self):
        """Assert Ga chooses Ultrasound.ga if both Lmp and Ultrasound provided."""
        ultrasound_dt = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt, reference_date=get_utcnow())
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_weeks_from_lmp_if_both_and_pref_lmp(self):
        """Assert Ga chooses Lmp.ga if both Lmp and Ultrasound provided but prefer_ultrasound=False."""
        ultrasound_dt = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt, reference_date=get_utcnow())
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound, prefer_ultrasound=False)
        self.assertEqual(ga.weeks, 17)
        self.assertEqual(ga.method, LMP)


class TestEdd(unittest.TestCase):

    def test_parmeters_for_edd_tests_below(self):
        """Assert parameters for tests below are correct."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=22)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        self.assertEqual(lmp.edd, datetime(2017, 2, 18))
        self.assertEqual(lmp.ga.weeks, 18)
        # US that calculates EDD within 7 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 15), ga_weeks=17)
        self.assertEqual((lmp.edd - ultrasound.edd).days, 7)
        # US that calculates EDD within 10 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 12), ga_weeks=17)
        self.assertEqual((lmp.edd - ultrasound.edd).days, 10)
        # US that calculates EDD within 11 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 11), ga_weeks=17)
        self.assertEqual((lmp.edd - ultrasound.edd).days, 11)
        self.assertEqual(datetime(2017, 2, 7), ultrasound.edd)

    def test_edd_favors_lmp_7days(self):
        """Asserts Edd for GA 16-21, with 7 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=22)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 15), ga_weeks=17)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 2, 18))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 7)

    def test_edd_favors_lmp_10days(self):
        """Asserts Edd for GA 16-21, with 10 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=22)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 12), ga_weeks=17)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 2, 18))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 10)

    def test_edd_favors_lmp_11days(self):
        """Asserts Edd for GA 16-21, with 11 days diff in edd calcs, uses Ultrasound.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=22)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 11), ga_weeks=17)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 2, 7))
        self.assertEqual(edd.method, ULTRASOUND)
        self.assertEqual(edd.diffdays, 11)

    def test_parmeters_for_edd_tests_below_ga22(self):
        """Assert parameters for tests below are correct."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=18)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        self.assertEqual(lmp.edd, datetime(2017, 3, 18))
        self.assertEqual(lmp.ga.weeks, 22)
        # US that calculates EDD within 13 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 21), ga_weeks=23)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 13)
        self.assertEqual(ultrasound.edd, datetime(2017, 3, 31))
        # US that calculates EDD within 14 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 22), ga_weeks=23)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 14)
        self.assertEqual(ultrasound.edd, datetime(2017, 4, 1))
        # US that calculates EDD within 15 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 23), ga_weeks=23)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 15)
        self.assertEqual(ultrasound.edd, datetime(2017, 4, 2))

    def test_edd_favors_lmp_13days_ga22(self):
        """Asserts Edd for GA 22-27, with 13 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=18)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 21), ga_weeks=23)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 3, 18))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 13)

    def test_edd_favors_lmp_14days_ga22(self):
        """Asserts Edd for GA 22-27, with 14 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=18)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 22), ga_weeks=23)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 3, 18))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 14)

    def test_edd_favors_lmp_15days_ga22(self):
        """Asserts Edd for GA 22-27, with 15 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=18)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 23), ga_weeks=23)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 4, 2))
        self.assertEqual(edd.method, ULTRASOUND)
        self.assertEqual(edd.diffdays, 15)

    def test_parmeters_for_edd_tests_below_ga27(self):
        """Assert parameters for tests below are correct."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=13)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        self.assertEqual(lmp.edd, datetime(2017, 4, 22))
        self.assertEqual(lmp.ga.weeks, 27)
        # US that calculates EDD within 13 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 28), ga_weeks=27)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 13)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 5))
        # US that calculates EDD within 14 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 29), ga_weeks=27)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 14)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 6))
        # US that calculates EDD within 15 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 10, 30), ga_weeks=27)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 15)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 7))

    def test_edd_favors_lmp_13days_ga27(self):
        """Asserts Edd for GA 27, with 13 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=13)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 28), ga_weeks=27)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 4, 22))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 13)

    def test_edd_favors_lmp_14days_ga27(self):
        """Asserts Edd for GA 27, with 14 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=13)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 29), ga_weeks=27)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 4, 22))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 14)

    def test_edd_favors_lmp_15days_ga27(self):
        """Asserts Edd for GA 27, with 15 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=13)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 10, 30), ga_weeks=27)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 5, 7))
        self.assertEqual(edd.method, ULTRASOUND)
        self.assertEqual(edd.diffdays, 15)

    def test_parmeters_for_edd_tests_below_ga28(self):
        """Assert parameters for tests below are correct."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=12)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        self.assertEqual(lmp.edd, datetime(2017, 4, 29))
        self.assertEqual(lmp.ga.weeks, 28)
        # US that calculates EDD within 13 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 11, 5), ga_weeks=28)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 21)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 20))
        # US that calculates EDD within 14 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 11, 6), ga_weeks=28)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 22)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 21))
        # US that calculates EDD within 15 days of lmp.edd
        ultrasound = Ultrasound(datetime(2016, 11, 7), ga_weeks=28)
        self.assertEqual(abs((lmp.edd - ultrasound.edd).days), 23)
        self.assertEqual(ultrasound.edd, datetime(2017, 5, 22))

    def test_edd_favors_lmp_21days_ga28(self):
        """Asserts Edd for GA 28, with 21 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=12)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 11, 5), ga_weeks=28)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 4, 29))
        self.assertEqual(edd.method, LMP)
        self.assertEqual(edd.diffdays, 21)

    def test_edd_favors_lmp_22days_ga28(self):
        """Asserts Edd for GA 28, with 21 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=12)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 11, 6), ga_weeks=28)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 5, 21))
        self.assertEqual(edd.method, ULTRASOUND)
        self.assertEqual(edd.diffdays, 22)

    def test_edd_favors_lmp_23days_ga28(self):
        """Asserts Edd for GA 28, with 21 days diff in edd calcs, uses Lmp.edd."""
        lmp_dt = datetime(2016, 10, 15) - relativedelta(weeks=12)
        lmp = Lmp(lmp=lmp_dt, reference_date=datetime(2016, 10, 15))
        ultrasound = Ultrasound(datetime(2016, 11, 7), ga_weeks=28)
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertEqual(edd.edd, datetime(2017, 5, 22))
        self.assertEqual(edd.method, ULTRASOUND)
        self.assertEqual(edd.diffdays, 23)
