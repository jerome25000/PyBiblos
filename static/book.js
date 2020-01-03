var app = new Vue({ 
    el: '#app',
    data: {
        message: 'Hello Vue!!!',
        authors : null,
        books : null,
        book1 : null
    },
    mounted: function() {
      axios
       .get('http://192.168.1.7/authors')
       .then(response => (this.authors = response.data.data))
       .catch(error => console.log(error))

       axios
       .get('http://192.168.1.7/books')
       .then(response => (this.books = response.data.data))
       .catch(error => console.log(error))

       axios
       .get('http://192.168.1.7/books/1')
       .then(response => (this.book1 = response))
       .catch(error => console.log(error))
    }
});
