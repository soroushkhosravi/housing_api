$(document).ready(function(){
    console.log('The page is loaded.');
    document.getElementById("submit").addEventListener(
    "click", function(event){
        console.log('abc');
        if (check_input_filled("post_code") === true){
		    $(".loader").show();
		    $(".container").hide();
        }
    }
    );
});

function check_input_filled(inputName){
	    if (document.getElementById(inputName).value.length === 0){
	        return false
        };
        return true
}