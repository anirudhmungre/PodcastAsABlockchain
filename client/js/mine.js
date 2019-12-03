let guess = 0;
let url = 'http://localhost:5000/mine';
let publicKey;

const mine = async() => {
    // console.log(`Guessing with ${guess}`)
    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ publicKey: publicKey, guess: guess })
    });
    let json = await response.json();
    // console.log(json.message);
    guess++;
    if (json.message != "Incorrect value! New block was not mined!") {
        console.log(json.message);
        guess = 0;
    }
    mine();
}

self.addEventListener('message', (e) => {
    publicKey = e.data;
    console.log(`Your Public Mining Key: ${publicKey}`)
    console.log('Starting to mine!');
    mine();
}, false);