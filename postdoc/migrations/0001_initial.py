from django.db import migrations, models
import django.db.models.deletion
import courselib.json_fields
import autoslug.fields
import courselib.storage
import postdoc.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('coredata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='postdoc_person',
                    to='coredata.person',
                )),
                ('unit', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='coredata.unit',
                )),
                ('supervisor', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='postdoc_supervisor',
                    to='coredata.person',
                )),
                ('secondary_supervisor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='postdoc_secondary_supervisor',
                    to='coredata.person',
                )),
                ('config', courselib.json_fields.JSONField(blank=False, default=dict, null=False)),
                ('type', models.CharField(max_length=24)),
                ('doctorate_completed_date', models.DateField()),
                ('work_eligibility_status', models.CharField(max_length=24)),
                ('relocation_reimbursement', models.BooleanField(default=False)),
                ('relocation_reimbursement_amount', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('involved_teaching', models.BooleanField(default=False)),
                ('other_info', models.CharField(blank=True, default='', max_length=500)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('benefits_estimation', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('work_hours', models.CharField(default='FULL_TIME', max_length=16)),
                ('hours_of_work', models.DecimalField(decimal_places=2, default=35, max_digits=5)),
                ('vacation_entitlement_weeks', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('annual_salary_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('lump_sum_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('fs1_unit', models.IntegerField(default=0)),
                ('fs1_fund', models.IntegerField(default=0)),
                ('fs1_project', models.CharField(blank=True, default='', max_length=10)),
                ('fs2_unit', models.IntegerField(default=0)),
                ('fs2_fund', models.IntegerField(default=0)),
                ('fs2_project', models.CharField(blank=True, default='', max_length=10)),
                ('fs3_unit', models.IntegerField(default=0)),
                ('fs3_fund', models.IntegerField(default=0)),
                ('fs3_project', models.CharField(blank=True, default='', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True)),
                ('last_updater', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='postdoc_last_updater', to='coredata.person')),
            ],
            options={
                'ordering': ['person__last_name', 'person__first_name'],
            },
        ),
        migrations.CreateModel(
            name='PostDocAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique_with=('appt',))),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contents', models.FileField(max_length=500, storage=courselib.storage.UploadedFileStorage, upload_to=postdoc.models.postdoc_attachment_upload_to)),
                ('mediatype', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('hidden', models.BooleanField(default=False, editable=False)),
                ('appt', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attachments', to='postdoc.postdoc')),
                ('created_by', models.ForeignKey(help_text='Attachment created by.', on_delete=django.db.models.deletion.PROTECT, to='coredata.person')),
            ],
            options={
                'ordering': ('created_at',),
                'unique_together': {('appt', 'slug')},
            },
        ),
    ]
