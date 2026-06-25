from coredata.models import SystemVariable

def get_contact_email(unit=None):
    return SystemVariable.get_value('ra_contact_email', unit)

def get_ra_intro_html(unit=None):
    return SystemVariable.get_value('ra_intro_html', unit)