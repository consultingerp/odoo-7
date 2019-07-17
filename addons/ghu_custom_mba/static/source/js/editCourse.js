new Vue({
    el: '#course',
    data () {
      return {
        course: null
      }
    },
    mounted () {
      axios
        .get('https://api.coindesk.com/v1/bpi/currentprice.json')
        .then(response => (this.course = response))
    }
  })