"use strict";

const serverUrl = "http://127.0.0.1:8000";

async function uploadImage() {
    // encode input file as base64 string for upload
    let file = document.getElementById("file").files[0];
    let converter = new Promise(function(resolve, reject) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result
            .toString().replace(/^data:(.*,)?/, ''));
        reader.onerror = (error) => reject(error);
    });
    let encodedString = await converter;

    // clear file upload input field
    document.getElementById("file").value = "";

    // make server call to upload image
    // and return the server upload promise
    return fetch(serverUrl + "/images", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({filename: file.name, filebytes: encodedString})
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new HttpError(response);
        }
    })
}

function updateImage(image) {
    document.getElementById("view").style.display = "block";

    let imageElem = document.getElementById("image");
    imageElem.src = image["fileUrl"];
    imageElem.alt = image["fileId"];

    return image;
}

function detectEmotion(image) {
    // make server call to translate image
    // and return the server upload promise
    return fetch(serverUrl + "/images/" + image["fileId"] + "/detect-emotion", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({fromLang: "auto", toLang: "en"})
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new HttpError(response);
        }
    })
}

function annotateImage(emotions) {
    let emotionsElem = document.getElementById("emotions");
    while (emotionsElem.firstChild) {
        emotionsElem.removeChild(emotionsElem.firstChild);
    }
    emotionsElem.clear
    let emotionText = ""
    for (let i = 0; i < emotions.length; i++) {
        let emotionElem = document.createElement("h6");
        emotionText = emotionText + " " + emotions[i];
        emotionElem.appendChild(document.createTextNode(
            emotions[i]
        ));
        
        emotionsElem.appendChild(document.createElement("hr"));
        emotionsElem.appendChild(emotionElem);
    }
    return emotionText
}

function readEmotion(emotionText) {
    let imageElem = document.getElementById("image");
    return fetch(serverUrl + "/images/" + imageElem.alt + "/read", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({text: emotionText})
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new HttpError(response);
        }
    })
}

function updateAudio(audio){
    let player = document.getElementById("player");
    let source = document.getElementById("audioSource");
    source.src = audio["fileUrl"];
    player.alt = audio["fileId"];
    player.load()
    player.play()
    
}


function uploadAndSense() {
    uploadImage()
        .then(image => updateImage(image))
        .then(image => detectEmotion(image))
        .then(emotions => annotateImage(emotions))
        .then(emotionText => readEmotion(emotionText))
        .then(audio => updateAudio(audio))
        .catch(error => {
            alert("Error: " + error);
        })
}

class HttpError extends Error {
    constructor(response) {
        super(`${response.status} for ${response.url}`);
        this.name = "HttpError";
        this.response = response;
    }
}