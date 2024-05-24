// "How many weeks do you plan to achieve your goal" slider
// With JQuery
$("#form-range-1").on("change", function() {
  console.log($("#form-range-1").val());
  $("#number-of-week").text($("#form-range-1").val());
});

// "How many hours can you dedicate" slider
// With JQuery
$("#form-range-2").on("change", function() {
  console.log($("#form-range-2").val());
  $("#number-of-hours-per-week").text($("#form-range-2").val());
});

// Click "Start Building" button, go to loading page
