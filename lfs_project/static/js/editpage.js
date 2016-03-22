$(document).ready(function(){
	$('#imageCreate').click(function(){

	      var link = $("#imageLink").val()

	      $('#imageLink').val('<img src="' + link + '"/>');

	});
});