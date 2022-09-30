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

    const template = `<span>
    {{#if quotaFull}}
      Please come back tomorrow.
    {{/if}}
    </span>`;
    const templateFunction = Handlebars.compile(template);
    const completedHtml = templateFunction({ quotaFull: true });
    document.getElementById('handle').innerHTML = completedHtml;
}