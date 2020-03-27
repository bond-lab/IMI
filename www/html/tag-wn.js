function toggle(myid) {
    if( document.getElementById(myid).style.display=='none'  ){
	document.getElementById(myid).style.display = '';
    }else{
	document.getElementById(myid).style.display = 'none';
    }
}
function check() {
    var inputs = document.getElementsByTagName('input');
    for (var i = 0; i < inputs.length; i += 1) {
	if(inputs[i].value = '')
	    inputs[i].disabled = true; 
    }
}
