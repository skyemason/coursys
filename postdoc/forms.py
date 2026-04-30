from django import forms
import datetime
from django.utils.html import format_html
from coredata.forms import PersonField
from postdoc.models import PostDoc, PostDocAttachment


class PostDocForm(forms.ModelForm):
    DEPT_CHOICES = (
        ('', '-----------'), (2110, '2110 (CMPT)'), (2130, '2130 (ENSC)'), (2140, '2140 (MSE)'), (2150, '2150 (SEE)'), (2020, "2020 (Dean's Office)"), (2030, "2030 (Dean's Office)")
    )

    FUND_CHOICES = (
        ('', '-----------'), (11, '11'), (13, '13'), (21, '21'), (23, '23'), (25, '25'), (29, '29'), (31, '31'), (32, '32'), (35, '35'), (36, '36'), (37, '37'), (38, '38'), (40, '40')
    )

    TYPE_CHOICES = (
        ('INTERNAL', 'Internal'),
        ('EXTERNAL_SFU', 'External (paid through SFU)'),
        ('EXTERNAL_NON_SFU', 'External (not paid through SFU)'),
        ('BOTH', 'Both Internal and External'),
    )

    WORK_ELIGIBILITY_STATUS_CHOICES = (
        ('CANADIAN_CITIZEN', 'Canadian Citizen'),
        ('PERMANENT_RESIDENT', 'Permanent Resident'),
        ('INTERNATIONAL', 'International'),
    )

    WORK_HOURS_CHOICES = (
        ('FULL_TIME', 'Full Time (35 hours/week)'),
        ('PART_TIME', 'Part Time'),
    )

    YES_NO_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )

    person = PersonField(label='PDF SFU ID', required=True)
    supervisor = PersonField(label='Hiring Supervisor Name', required=True)
    has_secondary_supervisor = forms.ChoiceField(
        label='Is there an additional supervisor?',
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial='N',
    )
    secondary_supervisor = PersonField(label='Secondary Hiring Supervisor Name', required=False)
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
    hours_of_work = forms.DecimalField(label='Hours of Work', required=False, min_value=0, decimal_places=2)
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
    fs1_unit = forms.ChoiceField(required=True, label='Department #1', choices=DEPT_CHOICES)
    fs1_fund = forms.TypedChoiceField(required=True, label='Fund #1', choices=FUND_CHOICES, coerce=int)
    fs1_project = forms.CharField(required=False, label='Project #1', help_text='Example: N654321, S654321, X654321, R654321. If fund 11, you may leave blank.')
    fs2_option = forms.BooleanField(required=False, label='Please select the following if there is an additional funding source')
    fs2_unit = forms.ChoiceField(required=False, label='Department #2', choices=DEPT_CHOICES)
    fs2_fund = forms.TypedChoiceField(required=False, label='Fund #2', choices=FUND_CHOICES, coerce=int)
    fs2_project = forms.CharField(required=False, label='Project #2', help_text='Example: N654321, S654321, X654321, R654321. If fund 11, you may leave blank.')
    fs3_option = forms.BooleanField(required=False, label='Please select the following if there is an additional funding source')
    fs3_unit = forms.ChoiceField(required=False, label='Department #3', choices=DEPT_CHOICES)
    fs3_fund = forms.TypedChoiceField(required=False, label='Fund #3', choices=FUND_CHOICES, coerce=int)
    fs3_project = forms.CharField(required=False, label='Project #3', help_text='Example: N654321, S654321, X654321, R654321. If fund 11, you may leave blank.')

    class Meta:
        model = PostDoc
        fields = (
            'person',
            'unit',
            'supervisor',
            'has_secondary_supervisor',
            'secondary_supervisor',
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
            'fs1_unit',
            'fs1_fund',
            'fs1_project',
            'fs2_option',
            'fs2_unit',
            'fs2_fund',
            'fs2_project',
            'fs3_option',
            'fs3_unit',
            'fs3_fund',
            'fs3_project',
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

        if cleaned_data.get('has_secondary_supervisor') == 'Y' and not cleaned_data.get('secondary_supervisor'):
            self.add_error('secondary_supervisor', 'You must answer this question.')
        if cleaned_data.get('has_secondary_supervisor') != 'Y':
            cleaned_data['secondary_supervisor'] = None

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

        project_exception_fund = 11

        if cleaned_data.get('fs1_fund') != project_exception_fund and not cleaned_data.get('fs1_project'):
            self.add_error('fs1_project', 'You must answer this question.')

        if cleaned_data.get('fs2_option'):
            error_message = 'If you have a second funding source then you must answer this question.'
            if not cleaned_data.get('fs2_unit'):
                self.add_error('fs2_unit', error_message)
            if cleaned_data.get('fs2_fund') in [None, '']:
                self.add_error('fs2_fund', error_message)
            if cleaned_data.get('fs2_fund') != project_exception_fund and not cleaned_data.get('fs2_project'):
                self.add_error('fs2_project', error_message)
        else:
            cleaned_data['fs2_unit'] = 0
            cleaned_data['fs2_fund'] = 0
            cleaned_data['fs2_project'] = ''

        if cleaned_data.get('fs3_option'):
            error_message = 'If you have a third funding source then you must answer this question.'
            if not cleaned_data.get('fs3_unit'):
                self.add_error('fs3_unit', error_message)
            if cleaned_data.get('fs3_fund') in [None, '']:
                self.add_error('fs3_fund', error_message)
            if cleaned_data.get('fs3_fund') != project_exception_fund and not cleaned_data.get('fs3_project'):
                self.add_error('fs3_project', error_message)
        else:
            cleaned_data['fs3_unit'] = 0
            cleaned_data['fs3_fund'] = 0
            cleaned_data['fs3_project'] = ''

        return cleaned_data


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
