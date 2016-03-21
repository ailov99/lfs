$("#acceptbutton").click(function(e) {
	$('#id_terms').prop('checked', true);
	$('#termsModal').modal('hide');
});