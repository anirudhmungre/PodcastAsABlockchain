let b64audio = '';

const generatePodcastCard = (title, media, posterKey, date) => {
    return `
        <div class="podcast-card">
            <div>
                <button class="btn-floating btn-large purple" onclick="playPodcast('${media}')">
                    <i class="material-icons">play_circle_filled</i>
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
            podcasts.forEach(p => {
                podList.innerHTML += generatePodcastCard(p.title, p.media, p.posterKey, p.date);
            });
        })
    });
};

const donate = (btn) => {
    btn.disabled = true;
    // TODO: Perform donation action
}

const playPodcast = (media) => {
    console.log(media);
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
            console.log(b64audio)
        };

        reader.readAsBinaryString(file);
    }
};

document.getElementById('audioUpload').addEventListener('change', handleAudioUpload, false);

loadPodcasts();