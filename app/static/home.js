window.onload = function(){
    function nameFormSubmit(){
        document.nameForm.action = '/second';
        document.nameForm.method = 'POST';
        sessionStorage.setItem('fname', document.getElementById('fname').value);
        sessionStorage.setItem('lname', document.getElementById('lname').value);
    }
    var button = document.getElementById('nameButton');
    button.onclick = function(){
        nameFormSubmit()};
}