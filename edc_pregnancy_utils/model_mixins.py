from uuid import uuid4

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import options
from django.utils import timezone

from django_crypto_fields.fields import EncryptedCharField
from edc_base.model.validators import date_not_future, datetime_not_future
from edc_constants.choices import GENDER_UNDETERMINED, YES_NO
from edc_identifier.maternal_identifier import MaternalIdentifier
from edc_protocol.validators import datetime_not_before_study_start
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin, SubjectIdentifierModelMixin


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('delivery_model', 'birth_model')


class BirthModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class LabourAndDeliveryModelMixin(models.Model):

    """A model mixin for Labour and Delivery models.

    If these field attrs don't exist, you may need to add properties to the concrete model.
    For example:

        @property
        def subject_type(self):
            return'maternal'

        @property
        def study_site(self):
            return self.subject_identifier[4:6]
    """

    reference = models.UUIDField(default=uuid4, editable=False)

    live_infants = models.IntegerField(
        verbose_name="How many live infants were delivered? ")

    live_infants_to_register = models.IntegerField(
        verbose_name="How many infants are you registering to the study? ")

    birth_orders = models.CharField(
        verbose_name="Birth order of infants to register, blank for ALL.",
        max_length=10,
        null=True,
        blank=True,
        help_text=(
            'Leave blank for all. If not blank, birth order numbers separated by commas, '
            'e.g. 2,3 for triplets where only the second and third baby are registering to the study.'))

    delivery_datetime = models.DateTimeField(
        verbose_name="Date and time of delivery :",
        help_text="If TIME unknown, estimate",
        validators=[
            datetime_not_future,
            datetime_not_before_study_start,
        ])

    delivery_time_estimated = models.CharField(
        verbose_name="Is the delivery TIME estimated?",
        max_length=3,
        choices=YES_NO)

    def save(self, *args, **kwargs):
        if self.subject_identifier:
            maternal_identifier = MaternalIdentifier(
                identifier=self.subject_identifier)
        else:
            maternal_identifier = MaternalIdentifier(
                subject_type_name=self.subject_type,
                model=self._meta.label_lower,
                study_site=self.study_site,
                last_name=self.last_name)
            self.subject_identifier = maternal_identifier.identifier
            maternal_identifier.deliver(
                self.live_infants,
                model=self._meta.birth_model,
                subject_type_name=self.subject_type,
                study_site=self.study_site,
                birth_orders=self.birth_orders)
        super(LabourAndDeliveryModelMixin, self).save(*args, **kwargs)

    @property
    def infants(self):
        infants = []
        if self.subject_identifier:
            maternal_identifier = MaternalIdentifier(
                identifier=self.subject_identifier)
            infants = maternal_identifier.infants
        return infants

    class Meta:
        abstract = True
        birth_model = None


class BirthModelMixin(SubjectIdentifierModelMixin, UpdatesOrCreatesRegistrationModelMixin, models.Model):

    delivery_reference = models.UUIDField()

    birth_order = models.IntegerField(
        validators=[MinValueValidator(1)])

    birth_order_denominator = models.IntegerField(
        validators=[MinValueValidator(1)])

    first_name = EncryptedCharField(
        max_length=25,
        verbose_name="Infant's first name",
        blank=True,
        help_text=(
            'Leave blank if not yet decided. If blank '
            'EDC will generate a temporary name'))

    initials = models.CharField(max_length=3, null=True)

    dob = models.DateField(
        verbose_name='Date of Birth',
        help_text="Must match labour and delivery report.",
        validators=[date_not_future, ])

    gender = models.CharField(
        max_length=10,
        choices=GENDER_UNDETERMINED)

    objects = BirthModelManager()

    def __str__(self):
        return "{}{} {} {}/{}".format(
            self.first_name,
            ' ({})'.format('' if self.first_name.startswith('Baby') else self.initials),
            self.gender, self.birth_order, self.birth_order_denominator)

    def save(self, *args, **kwargs):
        delivery_model = django_apps.get_model(*self._meta.delivery_model.split('.'))
        delivery = delivery_model.objects.get(reference=self.delivery_reference)
        maternal_identifier = MaternalIdentifier(identifier=delivery.subject_identifier)
        self.subject_identifier = maternal_identifier.infants[self.birth_order - 1].identifier
        if not self.first_name:
            RegisteredSubject = django_apps.get_app_config('edc_registration').model
            obj = RegisteredSubject.objects.get(subject_identifier=self.subject_identifier)
            self.first_name = obj.first_name
        if self.dob != timezone.localtime(delivery.delivery_datetime).date():
            raise ValidationError(
                'Infant date of birth must match date of delivery. Got {} != {}'.format(
                    self.dob, timezone.localtime(delivery.delivery_datetime).date()))
        return super(BirthModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    class Meta:
        abstract = True
        delivery_model = None
        unique_together = (
            ('delivery_reference', 'birth_order', 'birth_order_denominator'),
            ('delivery_reference', 'birth_order', 'birth_order_denominator', 'first_name')
        )
