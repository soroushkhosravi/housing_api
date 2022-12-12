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
            axios
              .get('/name')
              .then(response => (this.message = response.data))
       }
      }).mount('#app')
});