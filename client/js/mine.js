let guess = 0;
let url = 'http://localhost:5000/mine';
let publicKey;

const mine = async() => {
    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ publicKey: publicKey, guess: guess })
    });
    let json = await response.json();
    guess++;
    if (json.message != "Incorrect value! New block was not mined!") {
        postMessage(json.message);
        guess = 0;
    }
    mine();
}

self.addEventListener('message', (e) => {
    publicKey = e.data;
    postMessage(`Your Public Mining Key: ${publicKey}`)
    postMessage('Starting to mine!');
    mine();
}, false);