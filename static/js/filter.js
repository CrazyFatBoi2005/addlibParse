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
var installForm = document.getElementById("install-media-form");
var installBtn = document.getElementById("install-media-btn");


var socket = io.connect('http://127.0.0.1:5000');
var pageId = window.location.pathname.split('/')[2];
var key = 'buttonState_' + pageId;
var downloadMediaBtn = document.getElementById("download-media-btn");

function enableButton() {
  downloadMediaBtn.disabled = false;
  localStorage.setItem(key, "btnEnabled");

}

function disableButton() {
  downloadMediaBtn.disabled = true;
  localStorage.setItem(key, "btnDisabled");
}


window.addEventListener("load", function() {
  var buttonState = localStorage.getItem(key);

  if (buttonState === "btnEnabled") {
    enableButton();
  } else {
    disableButton();
  }
});

socket.on('disable_btn', function(data) {
    disableButton();
});


var textLoading = document.getElementById("loading-text");
installBtn.addEventListener('click', () => {
  var dots = 1; // Начальное количество точек

  function updateText() {
    textLoading.textContent = "Loading" + ".".repeat(dots);

    dots = (dots % 3) + 1;
  }

  var intervalId = setInterval(updateText, 500);

  socket.on('media_is_ready', function(data) {
    enableButton();
    clearInterval(intervalId);
    textLoading.textContent = "Ready!"
    console.log('Данные обновлены:', data);
});

});