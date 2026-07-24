from django import forms
import datetime
from django.utils.html import format_html
from django.forms import BaseInlineFormSet, inlineformset_factory
from coredata.forms import PersonField
from postdoc.models import PostDoc, PostDocAttachment, PostDocFundingSource, PostDocSupervisor


DEPT_CHOICES = (
    ('', '-----------'), (2110, '2110 (CMPT)'), (2130, '2130 (ENSC)'), (2140, '2140 (MSE)'), (2150, '2150 (SEE)'), (2020, "2020 (Dean's Office)"), (2030, "2030 (Dean's Office)")
)

FUND_CHOICES = (
    ('', '-----------'), (11, '11'), (13, '13'), (21, '21'), (23, '23'), (25, '25'), (29, '29'), (31, '31'), (32, '32'), (35, '35'), (36, '36'), (37, '37'), (38, '38'), (40, '40')
)

class PostDocForm(forms.ModelForm):

    TYPE_CHOICES = (
        ('INTERNAL', 'Internal'),
        ('EXTERNAL_SFU', 'External (paid through SFU)'),
        ('EXTERNAL_NON_SFU', 'External (not paid through SFU)'),
    )

    WORK_ELIGIBILITY_STATUS_CHOICES = (
        ('CANADIAN_CITIZEN', 'Canadian Citizen'),
        ('PERMANENT_RESIDENT', 'Permanent Resident'),
        ('INTERNATIONAL', 'International'),
    )

    WORK_HOURS_CHOICES = (
        ('FULL_TIME', 'Full Time (35 hours/week)'),
        ('PART_TIME', 'Part Time'),
        ('EXT', 'External'),
        ('LS', 'Lump Sum'),
    )

    YES_NO_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )

    person = PersonField(label='PDF SFU ID', required=True)
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=True)
    doctorate_completed_date = forms.DateField(label='Date Doctorate Completed', required=True)
    work_eligibility_status = forms.ChoiceField(
        choices=WORK_ELIGIBILITY_STATUS_CHOICES,
        required=True,
        help_text=format_html('<a id="postdoc-visa-link" href="#" style="display:none;"><b>+ Add New Visa</b></a>'),
    )
    relocation_reimbursement = forms.ChoiceField(
        label='Relocation Reimbursement?',
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial='N',
    )
    relocation_reimbursement_amount = forms.DecimalField(
        label='Relocation Reimbursement Amount',
        required=False,
        min_value=0,
        decimal_places=2,
    )
    involved_teaching = forms.ChoiceField(
        label='Involved teaching during Post Doc appointment?',
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial='N',
    )
    other_info = forms.CharField(
        label='Other information about the Appointee or Hiring Supervisor',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
    )
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    benefits_estimation = forms.DecimalField(label='Benefits Estimation %', required=False, min_value=0, decimal_places=2)
    work_hours = forms.ChoiceField(choices=WORK_HOURS_CHOICES, required=True)
    hours_of_work = forms.DecimalField(label='Hours of Work Per Week', required=False, min_value=0, decimal_places=2)
    vacation_entitlement_weeks = forms.DecimalField(label='Vacation Entitlement Per Year (in Weeks)', required=False, min_value=0, decimal_places=2)
    has_lump_sum_payment = forms.ChoiceField(
        label='Is this a lump sum payment?',
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )
    annual_salary_amount = forms.DecimalField(
        label='Annual Salary Amount',
        required=False,
        min_value=0,
        decimal_places=2,
    )
    lump_sum_payment = forms.DecimalField(
        label='Lump Sum Payment',
        required=False,
        min_value=0,
        decimal_places=2,
    )
    class Meta:
        model = PostDoc
        fields = (
            'person',
            'unit',
            'type',
            'doctorate_completed_date',
            'work_eligibility_status',
            'relocation_reimbursement',
            'relocation_reimbursement_amount',
            'involved_teaching',
            'other_info',
            'start_date',
            'end_date',
            'has_lump_sum_payment',
            'annual_salary_amount',
            'lump_sum_payment',
            'benefits_estimation',
            'work_hours',
            'hours_of_work',
            'vacation_entitlement_weeks',
        )
        labels = {
            'unit': 'Hiring Unit/School',
            'doctorate_completed_date': 'Date Doctorate Completed',
            'start_date': 'Appointment Start Date',
            'end_date': 'Appointment End Date',
        }

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super().is_valid(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        setattr(self.instance, 'fs2_option', cleaned_data.get('fs2_option', False))
        setattr(self.instance, 'fs3_option', cleaned_data.get('fs3_option', False))

        cleaned_data['relocation_reimbursement'] = cleaned_data.get('relocation_reimbursement') == 'Y'
        cleaned_data['involved_teaching'] = cleaned_data.get('involved_teaching') == 'Y'

        if cleaned_data.get('relocation_reimbursement'):
            reimbursement_amount = cleaned_data.get('relocation_reimbursement_amount')
            if reimbursement_amount is None:
                self.add_error('relocation_reimbursement_amount', 'You must answer this question.')
            elif reimbursement_amount <= 0:
                self.add_error('relocation_reimbursement_amount', 'Value must be greater than 0.')
        else:
            cleaned_data['relocation_reimbursement_amount'] = 0

        if cleaned_data.get('work_hours') == 'PART_TIME':
            hours_of_work = cleaned_data.get('hours_of_work')
            if hours_of_work is None:
                self.add_error('hours_of_work', 'You must answer this question.')
            elif hours_of_work <= 0:
                self.add_error('hours_of_work', 'Value must be greater than 0.')
        else:
            cleaned_data['hours_of_work'] = 35

        if cleaned_data.get('benefits_estimation') is None:
            cleaned_data['benefits_estimation'] = 0

        if cleaned_data.get('vacation_entitlement_weeks') is None:
            cleaned_data['vacation_entitlement_weeks'] = 0

        if cleaned_data.get('has_lump_sum_payment') == 'Y':
            lump_sum = cleaned_data.get('lump_sum_payment')
            if lump_sum is None:
                self.add_error('lump_sum_payment', 'You must answer this question.')
            elif lump_sum <= 0:
                self.add_error('lump_sum_payment', 'Value must be greater than 0.')
            cleaned_data['annual_salary_amount'] = None
        else:
            annual_salary = cleaned_data.get('annual_salary_amount')
            if annual_salary is None:
                self.add_error('annual_salary_amount', 'You must answer this question.')
            elif annual_salary <= 0:
                self.add_error('annual_salary_amount', 'Value must be greater than 0.')
            cleaned_data['lump_sum_payment'] = None

        return cleaned_data

class PostDocSupervisorForm(forms.ModelForm):
    supervisor = PersonField(label='Supervisor', required=False)

    class Meta:
        model = PostDocSupervisor
        fields = ('supervisor',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and getattr(self.instance, 'supervisor_id', None):
            sup = self.instance.supervisor
            if sup and sup.emplid:
                emplid = str(sup.emplid)
                self.initial['supervisor'] = emplid.zfill(9) if emplid.isdigit() else emplid

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super().is_valid(*args, **kwargs)


class BasePostDocSupervisorFormSet(BaseInlineFormSet):
    default_error_messages = {
        **BaseInlineFormSet.default_error_messages,
        'too_few_forms': 'Enter at least one supervisor.',
    }

    def clean(self):
        super().clean()
        kept = 0
        seen = set()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                continue

            sup = form.cleaned_data.get('supervisor')
            if not sup:
                continue

            kept += 1
            if sup.pk in seen:
                form.add_error('supervisor', 'Duplicate supervisor.')
            seen.add(sup.pk)

        if kept < 1:
            raise forms.ValidationError('At least one supervisor is required.')


PostDocSupervisorFormSet = inlineformset_factory(
    PostDoc,
    PostDocSupervisor,
    form=PostDocSupervisorForm,
    formset=BasePostDocSupervisorFormSet,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=3,
    validate_max=True,
)

class PostDocFundingSourceForm(forms.ModelForm):
    unit = forms.TypedChoiceField(choices=DEPT_CHOICES, coerce=int, empty_value=0, required=False, label='Department')
    fund = forms.TypedChoiceField(choices=FUND_CHOICES, coerce=int, empty_value=0, required=False, label='Fund')
    project = forms.CharField(required=False, label='Project')
    amount = forms.DecimalField(required=False, min_value=0, label='Amount')
    start_date = forms.DateField(required=False, label='Start date')
    end_date = forms.DateField(required=False, label='End date')


    class Meta:
        model = PostDocFundingSource
        fields = ('unit', 'fund', 'project', 'amount', 'start_date', 'end_date')

class BasePostDocFundingSourceFormSet(BaseInlineFormSet):
    default_error_messages = {
        **BaseInlineFormSet.default_error_messages,
        'too_few_forms': 'Enter at least one funding source.',
    }

    def clean(self):
        super().clean()
        project_exception_fund = 11
        kept = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            # built-in checkbox delete
            if form.cleaned_data.get('DELETE'):
                continue

            unit = form.cleaned_data.get('unit') or 0
            fund = form.cleaned_data.get('fund') or 0
            project = (form.cleaned_data.get('project') or '').strip()
            amount = form.cleaned_data.get('amount')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            is_blank = (unit == 0 and fund == 0 and not project and amount is None and not start_date and not end_date)

            # blank extra row: ignore
            if is_blank:
                continue

            kept += 1
            if unit == 0:
                form.add_error('unit', 'Required.')
            if fund == 0:
                form.add_error('fund', 'Required.')
            if fund != project_exception_fund and not project:
                form.add_error('project', 'Required unless fund is 11.')
            if start_date and end_date and end_date < start_date:
                form.add_error('end_date', 'End date must be on or after start date.')

        if kept == 0:
            raise forms.ValidationError('At least one funding source is required.')


PostDocFundingSourceFormSet = inlineformset_factory(
    PostDoc,
    PostDocFundingSource,
    form=PostDocFundingSourceForm,
    formset=BasePostDocFundingSourceFormSet,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=3,
    validate_max=True,
)

class PostDocNoteForm(forms.ModelForm):
    admin_notes = forms.CharField(required=False, label='Administrative Notes', widget=forms.Textarea)

    class Meta:
        model = PostDoc
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['admin_notes'] = getattr(self.instance, 'admin_notes')

    def clean(self):
        cleaned_data = super().clean()
        setattr(self.instance, 'admin_notes', cleaned_data['admin_notes'])
        return cleaned_data


class PostDocAdminAttachmentForm(forms.ModelForm):
    class Meta:
        model = PostDocAttachment
        exclude = ('appt', 'created_by')

class PostDocDownloadForm(forms.Form):
    BOOL_CHOICES = (('True', 'Yes'), ('False', 'No'))

    start_date = forms.DateField(
        label='Start Date Range (Begins)',
        widget=forms.DateInput(format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        required=True,
    )
    end_date = forms.DateField(
        label='Start Date Range (Ends)',
        help_text='PDFs in download will start within the indicated range.',
        widget=forms.DateInput(format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        required=True,
    )
    current = forms.ChoiceField(
        label='Only current PDFs (ignores above date range)',
        widget=forms.RadioSelect,
        choices=BOOL_CHOICES,
        initial='False',
        help_text='PDFs active now (or within two weeks).',
        required=False,
    )
    include_visa_status = forms.ChoiceField(
        label='Include Visas and Visa Expiries in Result',
        widget=forms.RadioSelect,
        choices=BOOL_CHOICES,
        initial='True',
        help_text='Include Visa Status',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(PostDocDownloadForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.initial['start_date'] = today - datetime.timedelta(days=1095)
        self.initial['end_date'] = today
