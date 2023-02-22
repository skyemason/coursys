var table;

function handle_form_change() {
  table.fnDraw();
}

function visa_browser_setup(my_url) {
  table = $('#visa_table').dataTable( {
    'jQueryUI': true,
    'pagingType': 'full_numbers',
    'pageLength' : 25,
    'processing': true,
    'serverSide': true,
    'sAjaxSource': my_url + '?tabledata=yes',
    'fnRowCallback': function( row ) {
        $('.visaexpired', row).closest('tr').addClass('visaexpired');
        $('.visaalmostexpired', row).closest('tr').addClass('visaalmostexpired');
        $('.visavalid', row).closest('tr').addClass('visavalid');
    },
  } );
}