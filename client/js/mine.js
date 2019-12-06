let guess = 0;
// URL to check if proof is correct
let url = 'http://localhost:5000/mine';
let publicKey;

// Mining happens async due to fetch requests
const mine = async() => {
    // Awaits response so doesnt make more attempts if correct
    // Makes a post request with the guess
    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ publicKey: publicKey, guess: guess })
    });
    let json = await response.json();
    // Makes new guess if incorrect
    guess++;
    if (json.message != "Incorrect value! New block was not mined!") {
        postMessage(json.message);
        // Restarts nonce guesses if correct
        guess = 0;
    }
    // Mines again with new guess
    mine();
}

// Starts to mine with sent public key
self.addEventListener('message', (e) => {
    publicKey = e.data;
    postMessage(`Your Public Mining Key: ${publicKey}`)
    postMessage('Starting to mine!');
    mine();
}, false);