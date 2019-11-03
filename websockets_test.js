socket= new WebSocket('ws://127.0.0.1');
socket.onopen= function() {
    socket.send('hello');
};
socket.onmessage= function(s) {
    console.log('got reply '+s);
};