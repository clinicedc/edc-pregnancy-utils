import unittest

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from faker import Faker

from django.apps import apps as django_apps
from django.test.testcases import TestCase

from edc_identifier.maternal_identifier import MaternalIdentifier
from edc_base_test.faker import EdcBaseProvider
from edc_base.utils import get_utcnow

from .constants import ULTRASOUND, LMP
from .edd import Edd
from .ga import Ga
from .lmp import Lmp
from .ultrasound import Ultrasound, UltrasoundError

fake = Faker()
fake.add_provider(EdcBaseProvider)


class TestModel(TestCase):
    """These were initially copied from edc_identifier."""
    def setUp(self):
        self.maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name())

    def test_maternal(self):
        self.assertIsNotNone(self.maternal_identifier.identifier)

    def test_deliver(self):
        self.maternal_identifier.deliver(1, model='edc_example.maternallabdel')
        self.assertEqual(self.maternal_identifier.infants[0].identifier, '000-40990001-6-10')

    def test_deliver_dont_create_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        self.maternal_identifier.deliver(1, model='edc_example.maternallabdel', create_registration=False)
        self.assertEqual(self.maternal_identifier.infants[0].identifier, '000-40990001-6-10')
        try:
            RegisteredSubject.objects.get(subject_identifier='000-40990001-6-10')
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')
        except RegisteredSubject.DoesNotExist:
            pass

    def test_deliver_create_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        self.maternal_identifier.deliver(1, model='edc_example.maternallabdel', create_registration=True)
        self.assertEqual(self.maternal_identifier.infants[0].identifier, '000-40990001-6-10')
        try:
            RegisteredSubject.objects.get(subject_identifier='000-40990001-6-10')
        except RegisteredSubject.DoesNotExist:
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')


class TestLmp(unittest.TestCase):

    def test_lmp_none(self):
        """Assert Lmp handles None."""
        lmp = Lmp()
        self.assertIsNone(lmp.edd)

    def test_lmp_edd(self):
        """Assert Lmp return edd."""
        dt = get_utcnow()
        edd = datetime.fromordinal((dt + relativedelta(days=280)).toordinal()).date()
        self.assertEqual(edd, Lmp(lmp=dt, reference_date=get_utcnow()).edd)

    def test_lmp_ga_minus(self):
        """Assert Lmp returns correct GA, decrement by days."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt)
        self.assertEqual(lmp.ga.weeks, 25)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt - relativedelta(days=5))
        self.assertEqual(lmp.ga.weeks, 24)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt - relativedelta(days=6))
        self.assertEqual(lmp.ga.weeks, 24)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt - relativedelta(days=7))
        self.assertEqual(lmp.ga.weeks, 24)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt - relativedelta(days=8))
        self.assertEqual(lmp.ga.weeks, 23)

    def test_lmp_ga_plus(self):
        """Assert Lmp returns correct GA, increment by days."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt)
        self.assertEqual(lmp.ga.weeks, 25)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt - relativedelta(days=1))
        self.assertEqual(lmp.ga.weeks, 24)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt + relativedelta(days=1))
        self.assertEqual(lmp.ga.weeks, 25)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt + relativedelta(days=2))
        self.assertEqual(lmp.ga.weeks, 25)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt + relativedelta(days=6))
        self.assertEqual(lmp.ga.weeks, 25)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt + relativedelta(days=7))
        self.assertEqual(lmp.ga.weeks, 26)
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt + relativedelta(days=8))
        self.assertEqual(lmp.ga.weeks, 26)


class TestUltrasound(unittest.TestCase):

    def test_ultrasound_edd(self):
        ultrasound_date = get_utcnow()
        for weeks in range(1, 40):
            for days in range(1, 7):
                ultrasound_edd = ultrasound_date + (relativedelta(weeks=40 - weeks) - relativedelta(days=days))
                try:
                    Ultrasound(
                        ultrasound_date,
                        ga_confirmed_weeks=weeks,
                        ga_confirmed_days=days,
                        ultrasound_edd=ultrasound_edd)
                except UltrasoundError as e:
                    self.fail(
                        'UltrasoundError unexpectedly raised for weeks={}, days={}. Got {}'.format(weeks, days, str(e)))

    def test_ultrasound_days_boundaries(self):
        """Assert Ultrasound raises errors for invalid days."""
        ultrasound_date = get_utcnow()
        try:
            Ultrasound(
                ultrasound_date,
                ga_confirmed_weeks=25,
                ga_confirmed_days=7,
                ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 25))
            self.fail('UltrasoundError not raised!')
        except UltrasoundError:
            pass

        try:
            Ultrasound(
                ultrasound_date,
                ga_confirmed_weeks=1,
                ga_confirmed_days=-1,
                ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 1))
            self.fail('UltrasoundError not raised!')
        except UltrasoundError:
            pass

    def test_ultrasound_weeks_boundaries(self):
        """Assert Ultrasound raises errors for invalid weeks."""
        ultrasound_date = get_utcnow()
        try:
            Ultrasound(
                ultrasound_date,
                ga_confirmed_weeks=-1,
                ga_confirmed_days=0,
                ultrasound_edd=ultrasound_date + relativedelta(weeks=40 + 1))
            self.fail('UltrasoundError not raised!')
        except UltrasoundError:
            pass
        try:
            Ultrasound(
                ultrasound_date,
                ga_confirmed_weeks=0,
                ga_confirmed_days=0,
                ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 0))
            self.fail('UltrasoundError not raised!')
        except UltrasoundError:
            pass
        try:
            Ultrasound(
                ultrasound_date,
                ga_confirmed_weeks=40,
                ga_confirmed_days=0,
                ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 40))
            self.fail('UltrasoundError not raised!')
        except UltrasoundError:
            pass

    def test_ultrasound_weeks_floor(self):
        """Assert ga weeks is rounded down to nearest int."""
        ultrasound_date = get_utcnow()
        for weeks in range(1, 40):
            for days in range(0, 7):
                ultrasound = Ultrasound(
                    ultrasound_date,
                    ga_confirmed_weeks=weeks,
                    ga_confirmed_days=days,
                    ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - weeks))
                self.assertEqual(weeks, ultrasound.ga.weeks)

    def test_ultrasound_none(self):
        """Assert Ultrasound can handle nulls."""
        ultrasound = Ultrasound()
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)
        ultrasound = Ultrasound(None, 25, 3)
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)

    def test_ultrasound_ga(self):
        """Assert Ultrasound returns ga in weeks, as is."""
        ultrasound_date = get_utcnow()
        ultrasound = Ultrasound(
            ultrasound_date=ultrasound_date,
            ga_confirmed_weeks=25,
            ga_confirmed_days=3,
            ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 25)
        )
        self.assertEqual(ultrasound.ga.weeks, 25)


class TestGa(unittest.TestCase):

    def test_ga_without_lmp_uses_ultrasound(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        ultrasound_date = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(
            ultrasound_date=ultrasound_date,
            ga_confirmed_weeks=25,
            ga_confirmed_days=3,
            ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 25)
        )
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

    def test_ga_confirmed_weeks_from_lmp(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        dt = get_utcnow()
        lmp = dt - (relativedelta(weeks=25) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp, reference_date=dt)
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, LMP)

    def test_ga_confirmed_weeks_from_ultrasound_if_both(self):
        """Assert Ga chooses Ultrasound.ga if both Lmp and Ultrasound provided."""
        ultrasound_date = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt, reference_date=get_utcnow())
        ultrasound = Ultrasound(
            ultrasound_date=ultrasound_date,
            ga_confirmed_weeks=25,
            ga_confirmed_days=3,
            ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 25)
        )
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_confirmed_weeks_from_lmp_if_both_and_pref_lmp(self):
        """Assert Ga chooses Lmp.ga if both Lmp and Ultrasound provided but prefer_ultrasound=False."""
        ultrasound_date = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt, reference_date=get_utcnow())
        ultrasound = Ultrasound(ultrasound_date, ga_confirmed_weeks=25)
        ga = Ga(lmp, ultrasound, prefer_ultrasound=False)
        self.assertEqual(ga.weeks, 23)
        self.assertEqual(ga.method, LMP)


class TestEdd(unittest.TestCase):

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
        ultrasound_date = get_utcnow().date()
        lmp = Lmp()
        ultrasound = Ultrasound(
            ultrasound_date=ultrasound_date,
            ga_confirmed_weeks=25,
            ultrasound_edd=ultrasound_date + relativedelta(weeks=40 - 25))
        edd = Edd(lmp, ultrasound)
        self.assertEqual(edd.edd, ultrasound.edd)
        self.assertEqual(edd.method, ULTRASOUND)


class TestEddFunctional(unittest.TestCase):

    def setUp(self):
        # {
        #   lmp_ga
        #       {case: (ultrasound_ga_confirmed_weeks, ultrasound_date_delta, expected_edd_diffdays, edd_choice) ...
        self.edds = {
            21: {
                7: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 11)},
                8: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 18)},
                9: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 18)},
                10: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 18)},
                11: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 18)},
                11: {'lmp_edd': date(2017, 2, 25), 'ultrasound_edd': date(2017, 2, 18)},
            },
        }

        self.parameters = {
            21: {
                7: (22, relativedelta(days=0), 7, 'lmp_edd', LMP),
                8: (22, relativedelta(days=1), 8, 'lmp_edd', LMP),
                9: (22, relativedelta(days=2), 9, 'lmp_edd', LMP),
                10: (22, relativedelta(days=3), 10, 'lmp_edd', LMP),
                11: (22, relativedelta(days=4), 11, 'ultrasound_edd', ULTRASOUND),
                12: (22, relativedelta(days=5), 12, 'ultrasound_edd', ULTRASOUND)
            },
        }
        self.reference_date = datetime(2016, 10, 15)
        # results
        self.lmp_edd = date(2017, 2, 18)
        self.ultrasound_edd = date(2017, 2, 7)

    def test_edd_parameter_cases(self):
        """Assert parameters for tests below are correct."""
        for ga_lmp in self.parameters:
            lmp_dt = self.reference_date - relativedelta(weeks=ga_lmp)
            lmp = Lmp(lmp=lmp_dt, reference_date=self.reference_date)
            for case, parameters in self.parameters.get(ga_lmp).items():
                ga_ultrasound, delta, diffdays, edd_attr, edd_method = parameters
                self.assertEqual(lmp.edd, self.edds.get(ga_lmp).get(case).get('lmp_edd'))
                self.assertEqual(lmp.ga.weeks, ga_lmp)
                ultrasound_date = self.reference_date - delta
                try:
                    ultrasound = Ultrasound(
                        ultrasound_date,
                        ga_confirmed_weeks=ga_ultrasound,
                        ultrasound_edd=self.edds.get(ga_lmp).get('ultrasound_edd'))
                except UltrasoundError as e:
                    raise UltrasoundError(
                        '{} {}.'.format(str(e), str([ga_ultrasound, delta, diffdays, edd_attr, edd_method])))
                self.assertEqual(
                    ultrasound.edd, self.edds.get(ga_lmp).get(case).get('ultrasound_edd'),
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
                self.assertEqual(
                    (lmp.edd - ultrasound.edd).days,
                    diffdays,
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
                self.assertEqual(
                    ultrasound.ga.weeks,
                    ga_ultrasound,
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
                # edd results
                edd = Edd(lmp=lmp, ultrasound=ultrasound)
                # assert Edd selects correct edd method
                self.assertEqual(
                    edd.method, edd_method,
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
                # assert Edd selects calculates correct edd diffdays
                self.assertEqual(
                    edd.diffdays, diffdays,
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
                # assert Edd selects correct edd
                self.assertEqual(
                    edd.edd, getattr(self, edd_attr),
                    msg=str([ga_ultrasound, delta, diffdays, edd_attr, edd_method]))
