
function connect(path) {
    var url = `ws://${window.location.host}/${path}`
    var ws = new WebSocket(url)

    ws.onopen = function() {
        this.send(`hello ${url} from browser`)
    }

    ws.onerror = function(event) {
        console.log(event)
        let span = document.getElementById('ws')
        span.innerText = 'error'
    }

    ws.onmessage = function(event) {
        console.log(event)
        let span = document.getElementById('ws')
        span.innerText = event.data
    }
}
