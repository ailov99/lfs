  $(document).ready(function(){
    $(document).on('change', '#category-select', function(){
  	currentChoice = $(this).find(':selected').text()
  	$( document.getElementById('title') ).html(currentChoice); //changes title of page to current shown leaderboard
  	var table = $(document.getElementById('table_id')).DataTable();
  	console.log(table);
  	table.search(currentChoice).draw();

  });


  $('#table_id').DataTable( {
  	"order": [[1]],
  	"oSearch": {"sSearch": "Overall"}
  });
  $('#category-select').removeAttr('selected').find('option:first').attr('selected', 'selected'); //resets select box to overall


  $('#user_list_table').DataTable( {
  	"order": [[0 , "asc"]],
  });
});