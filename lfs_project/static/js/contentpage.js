$(document).ready(function(){ 
  var pages = $(".module-page").length;
  var page = 1;
  $("#page"+page).show();
  $("#prev-page").hide();
  $("#back-btn").show();
  $("#quiz-btn").hide();
  if (page === pages) {
    		$("#next-page").hide();
        $("#quiz-btn").show();
  }
  var moduleid = $("#moduleid").attr('value');

  $("#next-page").click(function(){
      $.get('/lfs/update_progress/'+moduleid+'/'+page);
  	  $("#prev-page").show();
  	  $("#page"+page).hide();
      $("#back-btn").hide();
  	  page++;
      // if last page, show quiz button and hide next button
      if (page === pages) {
          $("#next-page").hide();
          $("#quiz-btn").show();
      }
      $("#page"+page).show();
  });
  $("#prev-page").click(function(){
  	  $("#next-page").show();
  	  $("#page"+page).hide();
      $("#quiz-btn").hide();
  	  page--;
      // if first page, show back button and hide prev button
      if (page === 1) {
          $("#prev-page").hide();
          $("#back-btn").show();
      }
      $("#page"+page).show();
  });
});