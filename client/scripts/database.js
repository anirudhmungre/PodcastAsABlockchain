const generatePodcastCard = (title, media, posterKey, date) => {
    return `
        <div class="podcast-card">
            <h2>${title}</h2>
            <p>${posterKey}</p>
            <p>${date}</p>
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

loadPodcasts();