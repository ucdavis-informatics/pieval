function changeClass() {
    document.getElementById("other-element").className = "active";
}


function toggleHideUnhideFullReportData(in_ele_id){
  var x = document.getElementById(in_ele_id);
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
