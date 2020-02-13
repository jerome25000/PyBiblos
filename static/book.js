Vue.component('paginate', VuejsPaginate)

var app = new Vue({ 
    el: '#app',
    data: {
        message: 'Hello Vue!!!',
        authors : null,
        books : null,
        book1 : null,
        pages : 15
    },
    methods: {
      click: function(page) {
        console.log(page)
      }
    },
    mounted: function() {
      axios
       .get('http://localhost/authors')
       .then(response => (this.authors = response.data.data))
       .catch(error => console.log(error));

       // axios
       // .get('http://localhost/books')
       // .then(response => (this.books = response.data.data))
       // .catch(error => console.log(error))

       // axios
       // .get('http://localhost/books/1')
       // .then(response => (this.book1 = response))
       // .catch(error => console.log(error))
    }
});


