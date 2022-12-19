$(document).ready(function(){
      const { createApp } = Vue
      createApp({
        data() {
          return {
            message: 'Hello Vue!'
          }
        },
        delimiters: ["[[", "]]"],
        compilerOptions: {
          delimiters: ["[[", "]]"]
        },
        mounted () {
//        Calls an endpoint and updates the item.
            axios
              .get('/name')
              .then(response => (this.message = response.data))
//          Listens for an event and updates the items
            window.addEventListener('my-event', (event) =>{
                this.message = event.detail.storage;
           })
       }
      }).mount('#app')
});