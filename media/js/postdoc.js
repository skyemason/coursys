// --- Utility show/hide helpers (mirrors ra_application.js pattern) ---

function hideInput(field) {
    $('label[for=id_' + field + '_0]').parent().hide();
    $('label[for=id_' + field + ']').parent().hide();
    $('#id_' + field).parent().parent().hide();
}

function showInput(field) {
    $('label[for=id_' + field + '_0]').parent().show();
    $('label[for=id_' + field + ']').parent().show();
    $('#id_' + field).parent().parent().show();
}

// --- Secondary supervisor toggle ---

function updateSecondarySupervisor() {
    if ($('input[name="has_secondary_supervisor"]:checked').val() === 'Y') {
        showInput('secondary_supervisor');
    } else {
        hideInput('secondary_supervisor');
        $('#id_secondary_supervisor').val('');
    }
}

function updateRelocationReimbursement() {
    if ($('input[name="relocation_reimbursement"]:checked').val() === 'Y') {
        showInput('relocation_reimbursement_amount');
    } else {
        hideInput('relocation_reimbursement_amount');
        $('#id_relocation_reimbursement_amount').val('0');
    }
}

function updateLumpSumPayment() {
    var lumpSumChoice = $('input[name="has_lump_sum_payment"]:checked').val();

    if (lumpSumChoice === 'Y') {
        hideInput('annual_salary_amount');
        showInput('lump_sum_payment');
    } else if (lumpSumChoice === 'N') {
        showInput('annual_salary_amount');
        hideInput('lump_sum_payment');
    } else {
        hideInput('annual_salary_amount');
        hideInput('lump_sum_payment');
    }
}

function updateWorkHours() {
    if ($('#id_work_hours').val() === 'PART_TIME') {
        showInput('hours_of_work');
    } else {
        hideInput('hours_of_work');
        $('#id_hours_of_work').val('35');
    }
}

function fs2ChoiceUpdate() {
    if ($('#id_fs2_option').is(':checked')) {
        $('.fs2').show();
    } else {
        $('.fs2').hide();
        $('.fs3').hide();
        $('#id_fs3_option').prop('checked', false);
    }
}

function fs3ChoiceUpdate() {
    if ($('#id_fs3_option').is(':checked')) {
        $('.fs3').show();
    } else {
        $('.fs3').hide();
    }
}

$(document).ready(function() {

    // Autocomplete for PDF SFU ID
    $('#id_person').autocomplete({
        source: '/data/students',
        minLength: 2,
        select: function(event, ui) {
            $(this).data('val', ui.item.value);
        }
    });

    // Autocomplete for Hiring Supervisor Name
    $('#id_supervisor').autocomplete({
        source: '/data/students',
        minLength: 2,
        select: function(event, ui) {
            $(this).data('val', ui.item.value);
        }
    });

    // Autocomplete for Secondary Hiring Supervisor Name
    $('#id_secondary_supervisor').autocomplete({
        source: '/data/students',
        minLength: 2,
        select: function(event, ui) {
            $(this).data('val', ui.item.value);
        }
    });

    // Set initial visibility of secondary supervisor field
    updateSecondarySupervisor();

    // Set initial visibility for relocation amount and salary/lump-sum fields
    updateRelocationReimbursement();
    updateLumpSumPayment();
    updateWorkHours();
    fs2ChoiceUpdate();
    fs3ChoiceUpdate();

    // Toggle secondary supervisor on radio change
    $('input[name="has_secondary_supervisor"]').change(function() {
        updateSecondarySupervisor();
    });

    $('input[name="relocation_reimbursement"]').change(function() {
        updateRelocationReimbursement();
    });

    $('input[name="has_lump_sum_payment"]').change(function() {
        updateLumpSumPayment();
    });

    $('#id_work_hours').change(function() {
        updateWorkHours();
    });

    $('#id_fs2_option').change(function() {
        fs2ChoiceUpdate();
    });

    $('#id_fs3_option').change(function() {
        fs3ChoiceUpdate();
    });

    $('#id_doctorate_completed_date').datepicker({'dateFormat': 'yy-mm-dd'});
    $('#id_start_date').datepicker({'dateFormat': 'yy-mm-dd'});
    $('#id_end_date').datepicker({'dateFormat': 'yy-mm-dd'});

});
