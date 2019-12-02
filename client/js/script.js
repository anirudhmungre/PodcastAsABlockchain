let b64audio = '';
let currentMedia;

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
                <button class="btn-floating btn-large green" onclick="donate(this)">
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

const donate = (btn) => {
    btn.disabled = true;
    // TODO: Perform donation action
}

const playPodcast = (btn, media) => {
    try {
        currentMedia = new Audio(`data:audio/wav;base64,${media}`);
        currentMedia.play();
        btn.style.display = 'none';
        let index = btn.id.match(/\d+/g).map(Number);
        document.getElementById(`pauseButton${index}`).style.display = 'initial';
    } catch (err) {
        alert('Something went wrong!');
        console.error(err);
    }
};

const pausePodcast = (btn) => {
    try {
        currentMedia.pause();
        currentMedia = null;
        let index = btn.id.match(/\d+/g).map(Number);
        btn.style.display = 'none';
        document.getElementById(`playButton${index}`).style.display = 'initial';
    } catch (err) {
        alert("Something went wrong!");
        console.error(err);
    }
};

const uploadPodcast = () => {
    let title = document.getElementById('title');
    let publicKey = document.getElementById('pubKey');
    if (title.value && publicKey.value && b64audio) {
        let url = 'http://localhost:5000/podcasts/add';
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title.value, media: b64audio, posterKey: publicKey.value })
        }).then(resp => {
            alert("Upload Successful!")
            b64audio = '';
            location.reload()
        });
    } else {
        alert('Please fill in all fields');
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