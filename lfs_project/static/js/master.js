$(document).ready(function(){
  $('#module-tabs a').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
  });
});

// Enable tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});
