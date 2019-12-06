// Initializes all materialize DOM elements including modal
M.AutoInit();

// Sets the main globals
let b64audio = '';
let currentMedia;
let mineWorker;

// Easier generation of toast message based on text
const toast = (text) => {
    M.toast({ html: text, classes: 'rounded' });
};

// Generates the card for each podcast using specified info
const generatePodcastCard = (title, media, posterKey, date, index) => {
    return `
        <div class="podcast-card">
            <div>
                <button id="playButton${index}" class="btn-floating btn-large purple" onclick="playPodcast(this, '${media}')">
                    <i class="material-icons">play_circle_filled</i>
                </button>
                <button id="pauseButton${index}" class="btn-floating btn-large purple" onclick="pausePodcast(this)" style="display: none;">
                    <i class="material-icons">pause_circle_filled</i>
                </button>
            </div>
            <div class="podcast-info">
                <h2>${title}</h2>
                <div>
                    <p>Created By: ${posterKey}</p>
                    <p>Created On: ${date}</p>
                </div>
            </div>
            <div class="donate">
                <button class="btn-floating btn-large green" onclick="openDonate('${posterKey}')">
                    <i class="material-icons">attach_money</i>
                </button>
            </div>
        </div>
    `
};

// Makes a request to receive all podcasts and fill podcast div
const loadPodcasts = () => {
    let podList = document.getElementById('podcasts');
    // Reset podcast div
    podList.innerHTML = '';
    let url = 'http://localhost:5000/podcasts';
    fetch(url).then(resp => {
        resp.json().then(podcasts => {
            let index = 0;
            podcasts.forEach(p => {
                // Add podcast cards for every podcast
                podList.innerHTML += generatePodcastCard(p.title, p.media, p.posterKey, p.date, index);
                index++;
            });
        })
    });
};

// Takes donation info and feeds to the server
const donate = () => {
    let amount = parseFloat(document.getElementById('amount').value);
    let posterKey = document.getElementById('sendTo').textContent;
    let publicKey = document.getElementById('publicKey').value;
    // Ensure amount values are correct for server
    if (amount > 0.01) {
        // Makes a donation request with correct info
        let url = 'http://localhost:5000/transactions/new';
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender: publicKey, recipient: posterKey, amount: amount })
        }).then(resp => {
            resp.json().then(data => {
                if (resp.status == 201) {
                    let instance = M.Modal.init(document.querySelector('.modal'))
                    instance.close();
                }
                toast(data.message);
            });
        });
    } else {
        // The amount was too small or incorrect
        toast('Enter an amount greater than 0.01 please.')
    }
};

// Opens the donation modal
const openDonate = (posterKey) => {
    // Checks if user has entererd their own public key
    let publicKey = document.getElementById('publicKey').value;
    if (publicKey) {
        // Opens the modal to enter info and amount
        let instance = M.Modal.init(document.querySelector('.modal'))
        instance.open();
        document.getElementById('sendTo').textContent = posterKey;
    } else {
        // User has not entered public key
        toast('Please enter your wallets public key to donate to a podcaster!');
    }
}

// Retrieves from server an updated amount in the current public key wallet
const refreshWallet = () => {
    // Gets DOM elements to change or utilize them
    let walletAmount = document.getElementById('walletAmount');
    let publicKey = document.getElementById('publicKey').value
        // Checks if user has a public key inserted
    if (publicKey) {
        // Requests the amount of the current wallet
        let url = 'http://localhost:5000/wallets/amount';
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ publicKey: publicKey })
        }).then(resp => {
            resp.json().then(data => {
                // Gets wallet amount or says wallet does not exist, dependant on server
                toast(data.message);
                walletAmount.textContent = data.amount;
            });
        });
    } else {
        // User does not have a public key inserted
        toast('Please input a public wallet key to check amount!');
    }
};

// Adds a new wallet of the given public key to the podchain
const addWallet = () => {
    let publicKey = document.getElementById('publicKey').value;
    // Checks if user entered wallet public key
    if (publicKey) {
        let url = 'http://localhost:5000/wallets/add';
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ publicKey: publicKey })
        }).then(resp => {
            resp.json().then(data => {
                // Adds the wallet or says it already exists dependant on server
                toast(data.message);
                // Refreshes shown wallet amount on screen
                refreshWallet();
            });
        });
    } else {
        // User has not entered wallet public key
        toast('Please input a public wallet key to add to podchain!');
    }
};

// Starts media player for podcast
const playPodcast = (btn, media) => {
    try {
        // If there is already media playing you cant start new media (must pause)
        if (currentMedia) { return; }
        // initializes a media player with the given base64 audio string
        currentMedia = new Audio(`data:audio/wav;base64,${media}`);
        let index = btn.id.match(/\d+/g).map(Number);
        // On ended event to stop mining as well as change button style to play again
        currentMedia.onended = () => {
            btn.style.display = 'initial';
            document.getElementById(`pauseButton${index}`).style.display = 'none';
            if (mineWorker) {
                mineWorker.terminate();
            }
        }

        // If user wants to mine they must have a public key for their wallet set
        // Else if user doesnt have public key set, don't play but direct them to set it
        // If user doesn't want to mine then just let em play the audio
        if (document.getElementById('wantMine').checked && document.getElementById('publicKey').value) {
            // Starts web worker to mine in the background while podcast is playing
            mineWorker = new Worker("js/mine.js");
            mineWorker.postMessage(document.getElementById('publicKey').value);
            mineWorker.onmessage = event => {
                toast(event.data);
            };
            // CHanges button so it shows pause while playing
            btn.style.display = 'none';
            document.getElementById(`pauseButton${index}`).style.display = 'initial';
            currentMedia.play();
        } else if (document.getElementById('wantMine').checked && !document.getElementById('publicKey').value) {
            // If user wants to mine but no public ke is set they are requested to set one
            toast("To mine please first input your PodCoin public key!");
            currentMedia = undefined;
        } else {
            // User is anon and doesn't want to mine, so they can just play the audio
            btn.style.display = 'none';
            document.getElementById(`pauseButton${index}`).style.display = 'initial';
            currentMedia.play();
        }
    } catch (err) {
        // Random error catch just in case
        toast('Something went wrong!');
        console.error(err);
    }
};

// Pauses the audio from a podcast that is playing
const pausePodcast = (btn) => {
    try {
        // Terminates the web worker in the background if they exist
        if (mineWorker) {
            mineWorker.terminate();
            mineWorker = undefined;
        }
        // Pauses the audio playing
        currentMedia.pause();
        currentMedia = null;
        // Changes the button of the designated podcast to play again
        let index = btn.id.match(/\d+/g).map(Number);
        btn.style.display = 'none';
        document.getElementById(`playButton${index}`).style.display = 'initial';
    } catch (err) {
        // Random error catch just in case
        toast("Something went wrong!");
        console.error(err);
    }
};

// User uploads a podcast based on required info
const uploadPodcast = () => {
    let title = document.getElementById('title').value;
    let posterKey = document.getElementById('posterKey').value;
    // Validates info was entered
    if (title && posterKey && b64audio) {
        // Makes request to add a new podcast
        let url = 'http://localhost:5000/podcasts/add';
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title, media: b64audio, posterKey: posterKey })
        }).then(resp => {
            if (resp.status == 200) {
                // If server responds 200 it means podcast upload was successful
                toast("Upload Successful!")
                b64audio = '';
                location.reload()
            }
        });
    } else {
        // User must fill in all fields and is prompted to do so
        toast('Please fill in all fields to upload!');
    }
};

// Manipulates the audio file to encode into base64 for storage in db
const handleAudioUpload = (event) => {
    let files = event.target.files;
    let file = files[0];

    if (files && file) {
        let reader = new FileReader();

        reader.onload = (readerEvent) => {
            let binaryString = readerEvent.target.result;
            b64audio = btoa(binaryString);
        };

        reader.readAsBinaryString(file);
    }
};
// Performs manipulation every time the audio file is changed on the upload
document.getElementById('audioUpload').addEventListener('change', handleAudioUpload, false);

// Initializes application by requesting all podcasts available
loadPodcasts();