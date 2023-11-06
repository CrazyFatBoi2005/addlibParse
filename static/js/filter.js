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
var params = new URLSearchParams(window.location.search);
var pageId = params.get('account_id');
var adStatus = params.get('ad_status')

var key = 'buttonState_' + pageId;
console.log(key);
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

var media_key = "mediaProcess_" + pageId + "_" + adStatus;
window.addEventListener("load", function() {
    var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");
    var checker_url = "http://127.0.0.1:8800/check_fully_download/" + acc_name + "?ad_status=" + adStatus
    function pollProgramStatusSt() {

            $.get(checker_url, function(data) {
                var status = data.status;
                var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");
                if (status) {
                    enableButton();
                    localStorage.setItem(media_key, "inactive");
                    return
                } else {
                    disableButton()
                }
                console.log(status);

            });
        }

        pollProgramStatusSt();
//  var buttonState = localStorage.getItem(key);
//    console.log(buttonState);
//  if (buttonState === "btnEnabled") {
//    enableButton();
//  } else {
//    disableButton();
//  }
});

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
    console.log(media_key);
  typeText();

  socket.on('media_is_ready', function(data) {
    enableButton();
    clearTimeout(typingInterval);
    textLoading.textContent = ""
    console.log('Данные обновлены:', data);
});

});


socket.on('disable_btn', function(data) {
    disableButton();
    textLoading.textContent = ""

});

document.addEventListener("DOMContentLoaded", function() {
    var mediaProcess = localStorage.getItem(media_key);
    console.log(mediaProcess);
    if (mediaProcess === "active") {
        var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");

        var checker_url = "http://127.0.0.1:8800/check_fully_download/" + acc_name + "?ad_status=" + adStatus
        typeText()
        function pollProgramStatus() {

            $.get(checker_url, function(data) {
                var status = data.status;
                var acc_name = document.getElementById("download-media-form__wrapper").getAttribute("data-acc-name");
                if (status) {
                    enableButton();
                    clearTimeout(typingInterval);
                    textLoading.textContent = "";
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

