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
    let response = fetch(url).then(resp => {
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

loadPodcasts();