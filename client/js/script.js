M.AutoInit();

let b64audio = '';
let currentMedia;
let mineWorker;

const toast = (text) => {
    M.toast({ html: text, classes: 'rounded' });
};

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

const loadPodcasts = () => {
    let podList = document.getElementById('podcasts')
    podList.innerHTML = '';
    let url = 'http://localhost:5000/podcasts';
    fetch(url).then(resp => {
        resp.json().then(podcasts => {
            let index = 0;
            podcasts.forEach(p => {
                podList.innerHTML += generatePodcastCard(p.title, p.media, p.posterKey, p.date, index);
                index++;
            });
        })
    });
};

const donate = () => {
    let amount = parseFloat(document.getElementById('amount').value);
    let posterKey = document.getElementById('sendTo').textContent;
    let publicKey = document.getElementById('publicKey').value;
    if (amount > 0.01) {
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
        toast('Enter an amount greater than 0.01 please.')
    }
};

const openDonate = (posterKey) => {
    let publicKey = document.getElementById('publicKey').value;
    if (publicKey) {
        let instance = M.Modal.init(document.querySelector('.modal'))
        instance.open();
        document.getElementById('sendTo').textContent = posterKey;
    } else {
        toast('Please enter your wallets public key to donate to a podcaster!');
    }
}

const refreshWallet = () => {
    let walletAmount = document.getElementById('walletAmount');
    let publicKey = document.getElementById('publicKey').value
    if (publicKey) {
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
                toast(data.message);
                walletAmount.textContent = data.amount;
            });
        });
    } else {
        toast('Please input a public wallet key to check amount!');
    }
};

const addWallet = () => {
    let publicKey = document.getElementById('publicKey').value
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
                toast(data.message);
                refreshWallet();
            });
        });
    } else {
        toast('Please input a public wallet key to add to podchain!');
    }
};

const playPodcast = (btn, media) => {
    try {
        if (currentMedia) { return; }
        currentMedia = new Audio(`data:audio/wav;base64,${media}`);
        let index = btn.id.match(/\d+/g).map(Number);
        currentMedia.onended = () => {
            btn.style.display = 'initial';
            document.getElementById(`pauseButton${index}`).style.display = 'none';
            if (mineWorker) {
                mineWorker.terminate();
            }
        }
        if (document.getElementById('wantMine').checked && document.getElementById('publicKey').value) {
            mineWorker = new Worker("js/mine.js");
            mineWorker.postMessage(document.getElementById('publicKey').value);
            mineWorker.onmessage = event => {
                toast(event.data);
            };
            btn.style.display = 'none';
            document.getElementById(`pauseButton${index}`).style.display = 'initial';
            currentMedia.play();
        } else if (document.getElementById('wantMine').checked && !document.getElementById('publicKey').value) {
            toast("To mine please first input your PodCoin public key!");
            currentMedia = undefined;
        } else {
            btn.style.display = 'none';
            document.getElementById(`pauseButton${index}`).style.display = 'initial';
            currentMedia.play();
        }
    } catch (err) {
        toast('Something went wrong!');
        console.error(err);
    }
};

const pausePodcast = (btn) => {
    try {
        if (mineWorker) {
            mineWorker.terminate();
            mineWorker = undefined;
        }
        currentMedia.pause();
        currentMedia = null;
        let index = btn.id.match(/\d+/g).map(Number);
        btn.style.display = 'none';
        document.getElementById(`playButton${index}`).style.display = 'initial';
    } catch (err) {
        toast("Something went wrong!");
        console.error(err);
    }
};

const uploadPodcast = () => {
    let title = document.getElementById('title').value;
    let posterKey = document.getElementById('posterKey').value;
    if (title && posterKey && b64audio) {
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
                toast("Upload Successful!")
                b64audio = '';
                location.reload()
            }
        });
    } else {
        toast('Please fill in all fields to upload!');
    }
};

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

document.getElementById('audioUpload').addEventListener('change', handleAudioUpload, false);

loadPodcasts();