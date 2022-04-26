const net = require('net');

const HOST = '127.0.0.1';
const PORT = 3520;

let client = new net.Socket();
client.connect(PORT, HOST, function()
{
    console.log("Sending data to my Python server");
    client.write(`VIDEO_${Date.now()}`);
});

client.on('data', function(data){
    console.log(`Data: ${data}`);
    client.destroy();
});

// Add a 'close' event handler for the client socket
client.on('close', function() {
    console.log('Connection closed');
});
  
