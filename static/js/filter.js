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
  downloadMediaBtn.classList.add("download-media-btn-active");
  localStorage.setItem(key, "btnEnabled");

}

function disableButton() {
  downloadMediaBtn.disabled = true;
  downloadMediaBtn.classList.remove("download-media-btn-active");
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

var media_key = "mediaProcess_" + pageId;
var textLoading = document.getElementById("loading-text");
var maxDots = 3;
var dots = 0;
function typeText() {
    textLoading.textContent = "Loading" + ".".repeat(dots);
    dots = (dots % maxDots) + 1;

    if (dots <= maxDots) {
        typingInterval = setTimeout(typeText, 500);
    }
}

installBtn.addEventListener('click', () => {
  localStorage.setItem(media_key, "active");

  typeText()

  socket.on('media_is_ready', function(data) {
    enableButton();
    clearTimeout(typingInterval);
    textLoading.textContent = "Ready!"
    console.log('Данные обновлены:', data);
});

});


document.addEventListener("DOMContentLoaded", function() {
    var mediaProcess = localStorage.getItem(media_key);
    console.log(mediaProcess);
    if (mediaProcess === "active") {
        var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");
        var checker_url = "http://127.0.0.1:8800/check_fully_download/" + acc_name
        typeText()
        function pollProgramStatus() {
            $.get(checker_url, function(data) {
                var status = data.status;
                var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");
                if (status) {
                    enableButton();
                    clearTimeout(typingInterval);
                    textLoading.textContent = "Ready!";
                    localStorage.setItem(media_key, "inactive");
                    return
                }
                console.log(status);

                setTimeout(pollProgramStatus, 5000);
            });
        }

        pollProgramStatus();
    }
});

