const express = require('express');
const bodyParser = require('body-parser');
const {dialogflow} = require('actions-on-google');

// Instantiate the Dialogflow client.
var conversation = dialogflow({debug: true});
var answerJson = {
  "conversationToken": "[]",
  "expectUserResponse": true,
  "expectedInputs": [
    {
      "inputPrompt": {
        "richInitialPrompt": {
          "items": [
            {
              "simpleResponse": {
                "textToSpeech": "Olá, tudo bem?"
              }
            }
          ]
        }
      },
      "possibleIntents": [
        {
          "intent": "assistant.intent.action.TEXT"
        }
      ]
    }
  ],
  "responseMetadata": {
    "status": {
      "message": "Success (200)"
    },
    "queryMatchInfo": {
      "queryMatched": true,
      "intent": "c6b8dee6-3459-4e2d-be09-d3f473f1eb54"
    }
  }
}

function setTextToSpeech(answerJson, newAnswerText){
    let input = answerJson["expectedInputs"][0]["inputPrompt"];
    let items = input["richInitialPrompt"]["items"];
    let simpleResponse = items[0]["simpleResponse"];
    simpleResponse["textToSpeech"] = newAnswerText;
}

//create an express app
const app = express();
//setup bodyparser middleware to handle JSON and urlencoded post requests
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

//this endpoint is really not needed, this is just to test if our server is accessible
app.get('/', (request, response) => {
    response.send(':)');
});

//this endpoint is where 'Google Assistant' is going to post messages whenever users interact with it.
app.post('/', (request, response) => {
    let body = request["body"];
    let rawInputs = body["inputs"][0]["rawInputs"];
    let query = rawInputs[0]["query"];
    
    setTextToSpeech(answerJson, query);
    response.send(answerJson);
});

//start the server to listen on port 3300
app.listen(3300, () => {
    console.log('app started listening on port', 3300);
});