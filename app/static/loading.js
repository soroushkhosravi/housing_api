$(document).ready(function(){
    console.log('The page is loaded.');
    document.getElementById("submit").addEventListener(
    "click", function(event){
        console.log('abc');
        $(".loader").show();
        $(".container").hide();
    }
    );
});