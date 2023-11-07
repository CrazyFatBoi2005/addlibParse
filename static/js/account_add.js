const closeAccountAddedModal = document.getElementById('close-account-added-modal');
const accountAddedModal = document.getElementById('account-added-modal');

var socket = io.connect('http://127.0.0.1:5000');

socket.on('data_updated', function(group_id) {
    var currentURL = window.location.pathname;
    var parts = currentURL.split('/');
    var groupIdUrl = parts[1];
    var groupIdUrlInt = parseInt(groupIdUrl);
    console.log(groupIdUrlInt);
    console.log(group_id);

    if (groupIdUrl === "" || groupIdUrl === "index") {
        if (group_id === 0) {
            window.location.href = window.location.href;
        } else {
            accountAddedModal.classList.add("show");
            var linkToGroup = document.getElementById('go-to-curr-group-id-link');
            if (group_id === 0) {
                linkToGroup.href = "/index"
            } else {
                linkToGroup.href = "/index/" + group_id
            }
            console.log(group_id);
        }
    } else {
        if (groupIdUrlInt === group_id) {
            window.location.href = window.location.href;
        } else {
            accountAddedModal.classList.add("show");
            var linkToGroup = document.getElementById('go-to-curr-group-id-link');
            if (group_id === 0) {
                linkToGroup.href = "/index"
            } else {
                linkToGroup.href = "/index/" + group_id
            }
            console.log(group_id);
        }
    }
});

closeAccountAddedModal.addEventListener('click', () => {
    accountAddedModal.style.display = 'none';
});