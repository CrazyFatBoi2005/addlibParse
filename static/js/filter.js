const openFilterBtn = document.getElementById('open-filter');
const closeFilterBtn = document.getElementById('close-filter');
const filterModal = document.getElementById('filter-window');

openFilterBtn.addEventListener('click', () => {
    filterModal.style.display = 'block';
});

closeFilterBtn.addEventListener('click', () => {
    filterModal.style.display = 'none';
});

var downloadModal = document.getElementById("download-modal");
var closeDownloadModal = document.getElementById("closeDownloadModal");
var downloadForm = document.getElementById("download-media-form");

downloadForm.addEventListener("submit", function(event) {
        downloadModal.classList.add("show");
        setTimeout(function() {
        downloadModal.classList.remove("show");
        downloadModal.classList.add("remove");
        }, 15000);
        setTimeout(function() {
            downloadModal.style.display = "none";
            modal.classList.remove("remove");
        }, 17000);

});

closeDownloadModal.addEventListener('click', () => {
    downloadModal.classList.remove("show");
});

var socket = io.connect('http://127.0.0.1:5000');

socket.on('media_is_ready', function(data) {
    location.reload()

    console.log('Данные обновлены:', data);
});

