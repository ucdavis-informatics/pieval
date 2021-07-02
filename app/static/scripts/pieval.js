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


function validateAnnotSelection(){
  tt = (element) => element;
  rbs = document.querySelectorAll('input[name="response"]');
  rb_checked = [];
  for(rb of rbs){
    rb_checked.push(rb.checked)
    console.log(rb.checked)
  }
  if(rb_checked.some(tt)){
      return true
  }else{
      alert("Select a value first!")
      return false
  }
}
