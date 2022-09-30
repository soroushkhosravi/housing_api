window.onload = function(){
    function setAttributesFromPreviousForm(){
          document.getElementById("fname").setAttribute('data-fname', sessionStorage.getItem('fname'));
          document.getElementById("lname").setAttribute('data-lname', sessionStorage.getItem('lname'));
          document.getElementById("fname").value = sessionStorage.getItem('fname');
          document.getElementById("lname").value = sessionStorage.getItem('lname');
    }
    function jobFormSubmit(){
        document.jobForm.action = '/third';
        document.jobForm.method = 'POST';
    }
    var button = document.getElementById('jobButton');

    setAttributesFromPreviousForm();
    button.onclick = function(){
        jobFormSubmit()};
}