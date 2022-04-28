const express = require('express');
const fs = require('fs');
const path = require('path')
const formidable = require('formidable');
const randomWords = require('random-words');
const net = require('net');

const HOST = '127.0.0.1';
const PORT = 3520;


const app = express();

const maxFileSizeInMB = 500;
const allowedExtensions = ['jpg', 'jpeg', 'png', 'mp4', 'avi']

app.post('/test', (req, res) =>{
    let word = randomWords()
    let client = new net.Socket();
    client.connect(PORT, HOST, function()
    {
        console.log("Sending data to my Python server");
        client.write(`VIDEO_${word}`);
    });

    client.on('data', function(data){
        console.log(`Data: ${data}`);
        client.destroy();
    });

    // Add a 'close' event handler for the client socket
    client.on('close', function() {
        console.log('Connection closed');
    });
    res.send(word);
});

app.post('/upload', (req, res) => {
    
    const form = new formidable.IncomingForm();
    form.maxFileSize = maxFileSizeInMB * 1024 * 1024;
    try
    {
        form.parse(req, function(err, fields, files){
            if (err)
            {
                res.writeHead(err.httpCode || 400, { 'Content-Type': 'text/plain' });
                res.end(String(err));
                return;        
            }
            // member of TableTennisVideo is for windows!!!
            let oldPath = String(files.TableTennisVideo.filepath);
            let newFileName = String(files.TableTennisVideo.originalFilename)
            let extension = newFileName.substring(newFileName.lastIndexOf("."))
            // reject invalid files
            if (extension.length == 0 || !allowedExtensions.includes(extension.substring(1)))
            {
                fs.unlink(oldPath);
                res.send("Rejected: uploaded disallowed files to this server.")
                return;        
            }
            // format: <shortenFileName>_<datetime>.<extension>
            let filenameWithoutExt = newFileName.substring(0, newFileName.lastIndexOf('.'));
            newFileName = `${filenameWithoutExt}_${Date.now()}${extension}`;
            
            // Sends socket messages to request process video
            let newPath = path.join(__dirname, 'upload_storage')
                    + '/'+ newFileName
            let rawData = fs.readFileSync(oldPath)
            
          
            fs.writeFile(newPath, rawData, function(err){
                if(err) console.log(err)

                let client = new net.Socket();
                client.connect(PORT, HOST, function()
                {
                    console.log("Sending data to my Python server");
                    client.write(`VIDEO_${newPath}`);
                });
            
                client.on('data', function(data){
                    console.log(`Data: ${data}`);
                    client.destroy();
                });
            
                // Add a 'close' event handler for the client socket
                client.on('close', function() {
                    console.log('Connection closed');
                });

                res.send("Successfully uploaded " + newFileName)
                //
            });
        });
    }
    catch
    {
        res.send("Unknown error occurred while trying to upload.");
    }
});

app.post('/download', (req, res) => {
    // TODO: List out downloadable videos
    res.send("The downloader will see you in the future!");
});
   
app.listen(3000, function(err){
    if(err) console.log(err)
    console.log('Server listening on Port 3000');
});