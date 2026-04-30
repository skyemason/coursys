from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib import messages
from courselib.auth import requires_role
from coredata.models import Person
from postdoc.forms import PostDocForm, PostDocNoteForm, PostDocAdminAttachmentForm, PostDocDownloadForm
from postdoc.models import PostDoc
from visas.models import Visa
import csv
import datetime


def _unit_choices(units):
    return [(u.id, u.name) for u in units]


def _emplid_value(person):
    if not person or not person.emplid:
        return ''
    emplid = str(person.emplid)
    return emplid.zfill(9) if emplid.isdigit() else emplid


def _postdoc_form_initial(appt):
    return {
        'person': _emplid_value(appt.person),
        'supervisor': _emplid_value(appt.supervisor),
        'secondary_supervisor': _emplid_value(appt.secondary_supervisor),
        'has_secondary_supervisor': 'Y' if appt.secondary_supervisor else 'N',
        'relocation_reimbursement': 'Y' if appt.relocation_reimbursement else 'N',
        'involved_teaching': 'Y' if appt.involved_teaching else 'N',
        'has_lump_sum_payment': 'Y' if appt.lump_sum_payment is not None else 'N',
    }


def _person_sortname_pref(person):
    if not person:
        return ''
    attr = getattr(person, 'sortname_pref', '')
    return attr() if callable(attr) else attr


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')


@requires_role('FDMA')
def post_doctoral_fellow(request):
    appointments = PostDoc.objects.filter(unit__in=request.units, deleted=False).select_related(
        'person', 'supervisor', 'secondary_supervisor', 'unit'
    ).order_by('-start_date', '-end_date')
    return render(request, 'postdoc/post_doctoral_fellow.html', {'appointments': appointments})


@requires_role('FDMA')
def view_postdoc_appointment(request, postdoc_slug):
    appt = get_object_or_404(PostDoc.objects.select_related('person', 'supervisor', 'secondary_supervisor', 'unit'),
                             slug=postdoc_slug, unit__in=request.units, deleted=False)
    return render(request, 'postdoc/view_postdoc_appointment.html', {'appt': appt, 'submission_author': appt.get_submission_author()})


@requires_role('FDMA')
def new_postdoc_appointment(request):
    if request.method == 'POST':
        form = PostDocForm(request.POST)
        form.fields['unit'].choices = _unit_choices(request.units)
        if form.is_valid():
            editor = get_object_or_404(Person, userid=request.user.username)
            appt = form.save(commit=False)
            appt.last_updater = editor
            if 'submission_author_id' not in appt.config:
                appt.config['submission_author_id'] = editor.id
            appt.save()
            return redirect('postdoc:post_doctoral_fellow')
    else:
        form = PostDocForm()
        form.fields['unit'].choices = _unit_choices(request.units)
    return render(request, 'postdoc/new_postdoc_appointment.html', {'form': form})


@requires_role('FDMA')
def edit_postdoc_appointment(request, postdoc_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    if request.method == 'POST':
        form = PostDocForm(request.POST, instance=appt)
        form.fields['unit'].choices = _unit_choices(request.units)
        if form.is_valid():
            editor = get_object_or_404(Person, userid=request.user.username)
            appt = form.save(commit=False)
            appt.last_updater = editor
            if 'submission_author_id' not in appt.config:
                appt.config['submission_author_id'] = editor.id
            appt.save()
            return redirect('postdoc:view_postdoc_appointment', postdoc_slug=appt.slug)
    else:
        form = PostDocForm(instance=appt, initial=_postdoc_form_initial(appt))
        form.fields['unit'].choices = _unit_choices(request.units)
    return render(request, 'postdoc/new_postdoc_appointment.html', {
        'form': form,
        'edit': True,
        'appt': appt,
    })


@requires_role('FDMA')
def edit_postdoc_notes(request, postdoc_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)

    if request.method == 'POST':
        noteform = PostDocNoteForm(request.POST, instance=appt)
        if noteform.is_valid():
            appt.last_updater = get_object_or_404(Person, userid=request.user.username)
            noteform.save()
            messages.success(request, 'Updated notes for ' + str(appt.person))
            return redirect('postdoc:view_postdoc_appointment', postdoc_slug=appt.slug)
    else:
        noteform = PostDocNoteForm(instance=appt)

    return render(request, 'postdoc/edit_postdoc_notes.html', {'noteform': noteform, 'appt': appt})


@requires_role('FDMA')
def new_admin_attachment(request, postdoc_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    editor = get_object_or_404(Person, userid=request.user.username)
    if request.method == 'POST':
        form = PostDocAdminAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.appt = appt
            attachment.created_by = editor
            upfile = request.FILES['contents']
            filetype = upfile.content_type
            if upfile.charset:
                filetype += '; charset=' + upfile.charset
            attachment.mediatype = filetype
            attachment.save()
            appt.last_updater = editor
            appt.save()
            messages.success(request, 'Attachment added.')
            return redirect('postdoc:view_postdoc_appointment', postdoc_slug=appt.slug)
    else:
        form = PostDocAdminAttachmentForm()

    return render(request, 'postdoc/new_postdoc_attachment.html', {'appt': appt, 'attachment_form': form})


@requires_role('FDMA')
def view_admin_attachment(request, postdoc_slug, attach_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    attachment = get_object_or_404(appt.attachments.visible(), slug=attach_slug)
    filename = attachment.contents.name.rsplit('/')[-1]
    response = StreamingHttpResponse(attachment.contents.chunks(), content_type=attachment.mediatype)
    response['Content-Disposition'] = 'inline; filename="' + filename + '"'
    response['Content-Length'] = attachment.contents.size
    return response


@requires_role('FDMA')
def download_admin_attachment(request, postdoc_slug, attach_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    attachment = get_object_or_404(appt.attachments.visible(), slug=attach_slug)
    filename = attachment.contents.name.rsplit('/')[-1]
    response = StreamingHttpResponse(attachment.contents.chunks(), content_type=attachment.mediatype)
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    response['Content-Length'] = attachment.contents.size
    return response


@requires_role('FDMA')
def delete_admin_attachment(request, postdoc_slug, attach_slug):
    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    attachment = get_object_or_404(appt.attachments.visible(), slug=attach_slug)
    attachment.hide()
    appt.last_updater = get_object_or_404(Person, userid=request.user.username)
    appt.save()
    messages.success(request, 'Attachment deleted.')
    return redirect('postdoc:view_postdoc_appointment', postdoc_slug=appt.slug)


@requires_role('FDMA')
def delete_postdoc_appointment(request, postdoc_slug):
    if request.method != 'POST':
        return HttpResponse(status=405)

    appt = get_object_or_404(PostDoc, slug=postdoc_slug, unit__in=request.units, deleted=False)
    appt.deleted = True
    appt.last_updater = get_object_or_404(Person, userid=request.user.username)
    appt.save()

    messages.success(request, 'Post Doc appointment deleted.')
    return redirect('postdoc:post_doctoral_fellow')


@requires_role('FDMA')
def download_index(request):
    form = PostDocDownloadForm(request.POST or None)
    start_date = form.initial['start_date']
    end_date = form.initial['end_date']
    current = False
    include_visa_status = True

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        current = _to_bool(form.cleaned_data.get('current'))
        include_visa_status = _to_bool(form.cleaned_data.get('include_visa_status'), default=True)

    context = {
        'form': form,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'current': current,
        'include_visa_status': include_visa_status,
    }
    return render(request, 'postdoc/download_index.html', context)


@requires_role('FDMA')
def download_admin(request):
    today = datetime.date.today()
    start_date_raw = request.GET.get('start_date', (today - datetime.timedelta(days=1095)).strftime('%Y-%m-%d'))
    end_date_raw = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    current = _to_bool(request.GET.get('current'))
    include_visa_status = _to_bool(request.GET.get('include_visa_status'), default=True)

    try:
        start_date = datetime.datetime.strptime(start_date_raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        start_date = today - datetime.timedelta(days=1095)
    try:
        end_date = datetime.datetime.strptime(end_date_raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        end_date = today

    appts = PostDoc.objects.filter(unit__in=request.units, deleted=False).select_related(
        'person', 'supervisor', 'secondary_supervisor', 'unit'
    )

    if current:
        slack = 14
        appts = appts.filter(start_date__lte=today + datetime.timedelta(days=slack), end_date__gte=today - datetime.timedelta(days=slack))
    else:
        appts = appts.filter(start_date__gte=start_date, start_date__lte=end_date)

    appts = appts.order_by('start_date', 'person__last_name', 'person__first_name')
    results = list(appts)

    response = HttpResponse(content_type='text/csv')
    date_tag = datetime.datetime.now().strftime('%m%d%Y')
    if len(results) == 1:
        filename = 'pdf-%s-%s.csv' % (results[0].slug, date_tag)
    else:
        filename = 'pdfs-%s.csv' % date_tag
    response['Content-Disposition'] = 'inline; filename="%s"' % filename

    visa_columns = []
    if include_visa_status:
        visa_columns = ['Most Recent Visa Type', 'Most Recent Visa Expiry Date']

    writer = csv.writer(response)
    writer.writerow([
        'Hiring Department (Unit)',
        'Supervisor Name',
        'Supervisor SFU ID',
        'Supervisor Email',
        'Secondary Supervisor Name',
        'Secondary Supervisor ID',
        'Secondary Supervisor Email',
        'Funding Source 1 Department',
        'Funding Source 1 Fund',
        'Funding Source 1 Project',
        'Funding Source 2 Department',
        'Funding Source 2 Fund',
        'Funding Source 2 Project',
        'Funding Source 3 Department',
        'Funding Source 3 Fund',
        'Funding Source 3 Project',
        'PDF Name',
        'PDF SFU ID',
        'PDF Email',
    ] + visa_columns + [
        'Start Date',
        'End Date',
        'Pay Amount',
        'Payment Type',
    ])

    for appt in results:
        secondary_name = ''
        secondary_id = ''
        secondary_email = ''
        if appt.secondary_supervisor:
            secondary_name = _person_sortname_pref(appt.secondary_supervisor)
            secondary_id = appt.secondary_supervisor.emplid or ''
            secondary_email = appt.secondary_supervisor.email() or ''

        visa_values = []
        if include_visa_status:
            recent_visa = Visa.objects.visible().filter(person=appt.person).order_by('-end_date').first()
            if recent_visa:
                visa_values = [recent_visa.status or '', recent_visa.end_date or '']
            else:
                visa_values = ['', '']

        pay_amount = ''
        payment_type = ''
        if appt.lump_sum_payment is not None:
            pay_amount = appt.lump_sum_payment
            payment_type = 'Lump Sum'
        elif appt.annual_salary_amount is not None:
            pay_amount = appt.annual_salary_amount
            payment_type = 'Annual Salary'

        writer.writerow([
            appt.unit.label if appt.unit else '',
            _person_sortname_pref(appt.supervisor),
            appt.supervisor.emplid if appt.supervisor and appt.supervisor.emplid else '',
            appt.supervisor.email() if appt.supervisor else '',
            secondary_name,
            secondary_id,
            secondary_email,
            appt.fs1_unit or '',
            appt.fs1_fund or '',
            appt.fs1_project or '',
            appt.fs2_unit if appt.fs2_option else '',
            appt.fs2_fund if appt.fs2_option else '',
            appt.fs2_project if appt.fs2_option else '',
            appt.fs3_unit if appt.fs3_option else '',
            appt.fs3_fund if appt.fs3_option else '',
            appt.fs3_project if appt.fs3_option else '',
            _person_sortname_pref(appt.person),
            appt.person.emplid if appt.person and appt.person.emplid else '',
            appt.person.email() if appt.person else '',
        ] + visa_values + [
            appt.start_date,
            appt.end_date,
            pay_amount,
            payment_type,
        ])

    return response
