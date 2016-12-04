from uuid import uuid4

from django.apps import apps as django_apps
from django.db import models
from django.db.models import options

from django_crypto_fields.fields.encrypted_char_field import EncryptedCharField
from edc_registration.model_mixins import (
    UpdatesOrCreatesRegistrationModelMixin, SubjectIdentifierModelMixin, AllocateSubjectIdentifierMixin)
from edc_constants.choices import GENDER_UNDETERMINED, YES_NO
from edc_base.model.validators.date import date_not_future, datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from django.utils import timezone
from edc_identifier.maternal_identifier import MaternalIdentifier


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('delivery_model',)


class BirthModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class LabourAndDeliveryMixin(models.Model):

    reference = models.UUIDField(default=uuid4, editable=False)

    live_infants = models.IntegerField()

    live_infants_to_register = models.IntegerField(
        verbose_name="How many infants are you registering to the study? ")

    birth_orders = models.CharField(
        verbose_name="List birth order of infants to register separated by commas, or leave blank for all.",
        null=True,
        blank=True,
        help_text='For example, ')

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        help_text='')

    delivery_datetime = models.DateTimeField(
        verbose_name="Date and time of delivery :",
        help_text="If TIME unknown, estimate",
        validators=[
            datetime_not_future, ])

    delivery_time_estimated = models.CharField(
        verbose_name="Is the delivery TIME estimated?",
        max_length=3,
        choices=YES_NO)

    delivery_comment = models.TextField(
        verbose_name="List any additional information about the labour and delivery (mother only) ",
        max_length=250,
        blank=True,
        null=True)

    def save(self, *args, **kwargs):
        maternal_identifier = MaternalIdentifier()
        self.subject_identifier = maternal_identifier.identifier
        maternal_identifier.deliver(self.live_infants)
        super(LabourAndDeliveryMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class BirthMixin(SubjectIdentifierModelMixin, AllocateSubjectIdentifierMixin,
                 UpdatesOrCreatesRegistrationModelMixin, models.Model):

    delivery_reference = models.UUIDField()

    birth_order = models.IntegerField()

    birth_order_denominator = models.IntegerField()

    singleton = models.BooleanField(default=True)

    report_datetime = models.DateTimeField(
        verbose_name="Date and Time Infant Enrolled",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ])

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
        if not self.first_name:
            self.first_name = 'Baby{}{}'.format(str(self.birth_order, self.mother.lastname.lower().title()))
        delivery_model = django_apps.get_model(*self._meta.delivery_model.split('.'))
        delivery = delivery_model.objects.get(reference=self.delivery_reference)
        maternal_identifier = MaternalIdentifier(identifier=delivery.maternal_identifier)
        self.subject_identifier = maternal_identifier.infants[self.birth_order]
        
        
        else:
        if self.dob != tz_local.self.delivery.delivery_datetime.
        if self.singleton:
            self.birth_order = 1
            self.birth_order_denominator = 1
        else:
            
        return super(BirthMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    @property
    def mother(self):
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        return RegisteredSubject.objects.get(subject_identifier=self.delivery.subject_identifier)

    @property
    def delivery(self):
        delivery_model = django_apps.get_model(*self._meta.delivery_model)
        return delivery_model.objects.get(reference=self.delivery_reference)

    class Meta:
        abstract = True
        visit_schedule_name = None
        delivery_model = None
        unique_together = (
            ('delivery_reference', 'birth_order', 'birth_order_denominator'),
            ('delivery_reference', 'birth_order', 'birth_order_denominator', 'first_name')
        )
