function changeClass() {
    document.getElementById("other-element").className = "active";
}


function toggleHideUnhideFullReportData(in_ele_id, in_form_cell_id){
  var x = document.getElementById(in_ele_id);
  var y = document.getElementById("context_viewed");
  if (x.style.display === "none") {
    x.style.display = "block";
    y.value = 'yes';
  } else {
    x.style.display = "none";
  }
}
