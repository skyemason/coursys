from django.db import models
from django.urls import reverse
import os
from coredata.models import Person, Unit
from courselib.json_fields import JSONField, config_property
from autoslug import AutoSlugField
from courselib.slugs import make_slug
from courselib.storage import UploadedFileStorage, upload_path


def postdoc_attachment_upload_to(instance, filename):
    return upload_path('postdocattachments', filename)


class PostDocAttachmentQueryset(models.QuerySet):
    def visible(self):
        return self.filter(hidden=False)


class PostDoc(models.Model):
    TYPE_LABELS = {
        'INTERNAL': 'Internal',
        'EXTERNAL_SFU': 'External (paid through SFU)',
        'EXTERNAL_NON_SFU': 'External (not paid through SFU)',
        'BOTH': 'Both Internal and External',
    }

    WORK_ELIGIBILITY_STATUS_LABELS = {
        'CANADIAN_CITIZEN': 'Canadian Citizen',
        'PERMANENT_RESIDENT': 'Permanent Resident',
        'INTERNATIONAL': 'International',
    }

    WORK_HOURS_LABELS = {
        'FULL_TIME': 'Full Time (35 hours/week)',
        'PART_TIME': 'Part Time',
    }

    person = models.ForeignKey(
        Person,
        related_name='postdoc_person',
        on_delete=models.PROTECT,
        null=False,
    )
    unit = models.ForeignKey(
        Unit,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )
    supervisor = models.ForeignKey(
        Person,
        related_name='postdoc_supervisor',
        on_delete=models.PROTECT,
        null=False,
    )
    secondary_supervisor = models.ForeignKey(
        Person,
        related_name='postdoc_secondary_supervisor',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    config = JSONField(null=False, blank=False, default=dict)
    type = models.CharField(max_length=24)
    doctorate_completed_date = models.DateField()
    work_eligibility_status = models.CharField(max_length=24)
    relocation_reimbursement = models.BooleanField(default=False)
    relocation_reimbursement_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    involved_teaching = models.BooleanField(default=False)
    other_info = models.CharField(max_length=500, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    benefits_estimation = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    work_hours = models.CharField(max_length=16, default='FULL_TIME')
    hours_of_work = models.DecimalField(max_digits=5, decimal_places=2, default=35)
    vacation_entitlement_weeks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    annual_salary_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    lump_sum_payment = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    fs1_unit = models.IntegerField(default=0)
    fs1_fund = models.IntegerField(default=0)
    fs1_project = models.CharField(max_length=10, default='', blank=True)
    fs2_option = config_property('fs2_option', default=False)
    fs2_unit = models.IntegerField(default=0)
    fs2_fund = models.IntegerField(default=0)
    fs2_project = models.CharField(max_length=10, default='', blank=True)
    fs3_option = config_property('fs3_option', default=False)
    fs3_unit = models.IntegerField(default=0)
    fs3_fund = models.IntegerField(default=0)
    fs3_project = models.CharField(max_length=10, default='', blank=True)
    admin_notes = config_property('admin_notes', default='')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updater = models.ForeignKey(
        Person,
        related_name='postdoc_last_updater',
        default=None,
        on_delete=models.PROTECT,
        null=True,
        editable=False,
    )

    def autoslug(self):
        if self.person.userid:
            ident = self.person.userid
        else:
            ident = str(self.person.emplid)
        return make_slug('pdf' + '-' + str(self.start_date.year) + '-' + ident)

    slug = AutoSlugField(populate_from='autoslug', null=False, editable=False, unique=True)

    class Meta:
        ordering = ['person__last_name', 'person__first_name']

    def get_absolute_url(self):
        return reverse('postdoc:view_postdoc_appointment', kwargs={'postdoc_slug': self.slug})

    def has_attachments(self):
        return self.attachments.visible().exists()

    def get_submission_author(self):
        person_id = self.config.get('submission_author_id')
        if person_id:
            return Person.objects.filter(id=person_id).first()
        return self.last_updater

    def get_type_label(self):
        return self.TYPE_LABELS.get(self.type, self.type)

    def get_work_eligibility_status_label(self):
        return self.WORK_ELIGIBILITY_STATUS_LABELS.get(self.work_eligibility_status, self.work_eligibility_status)

    def get_work_hours_label(self):
        return self.WORK_HOURS_LABELS.get(self.work_hours, self.work_hours)

    def __str__(self):
        return f'{self.person} — {self.unit}'


class PostDocAttachment(models.Model):
    appt = models.ForeignKey(PostDoc, null=False, blank=False, related_name='attachments', on_delete=models.PROTECT)
    title = models.CharField(max_length=250, null=False)
    slug = AutoSlugField(populate_from='title', null=False, editable=False, unique_with=('appt',))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Person, help_text='Attachment created by.', on_delete=models.PROTECT)
    contents = models.FileField(storage=UploadedFileStorage, upload_to=postdoc_attachment_upload_to, max_length=500)
    mediatype = models.CharField(max_length=200, null=True, blank=True, editable=False)
    hidden = models.BooleanField(default=False, editable=False)

    objects = PostDocAttachmentQueryset.as_manager()

    class Meta:
        ordering = ('created_at',)
        unique_together = (('appt', 'slug'),)

    def __str__(self):
        return self.contents.name + ' titled ' + self.title + ', for ' + str(self.appt)

    def contents_filename(self):
        return os.path.basename(self.contents.name)

    def hide(self):
        self.hidden = True
        self.save()
