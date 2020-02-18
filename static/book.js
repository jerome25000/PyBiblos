Vue.component('paginate', VuejsPaginate)

var app = new Vue({ 
    el: '#app',
    data: {
        authors : null,
        pageNumber : 10,
        pageSize : 20,
        pageTotal : 20,
        serverUrl : null,
    },
    methods: {
      getAuthors : function(pageNumber) {
        this.pageNumber = pageNumber;
        axios
         .get(this.serverUrl + '/authors?pageNumber=' + this.pageNumber + '&pageSize=' + this.pageSize)
         .then(response => {
            this.authors = response.data.data;
            this.pageTotal = response.data.pagination.pageTotal;
          })
         .catch(error => console.log(error))
      }
    },
    created:function () {
        this.serverUrl = window.location.origin;
        this.getAuthors(this.pageNumber);
    },
});


