const openModalBtn = document.getElementById('open-modal');
const closeModalBtn = document.getElementById('close-modal');
const modal = document.getElementById('modal-window');
var form = document.getElementById("add-page-form");
var modal1 = document.getElementById("modal");
var closeModalNotif = document.getElementById("closeModal");

openModalBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

closeModalBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

form.addEventListener("submit", function(event) {
        modal.style.display = 'none';
        modal1.classList.add("show");
        var modal1P = document.getElementById('modal-text')
        modal1.classList.remove("red-color-modal")
        modal1P.textContent = "Account will be added soon!"

});

closeModalNotif.addEventListener('click', () => {
    modal1.style.display = 'none';
});


var socket = io.connect('http://178.253.42.33:5000');

socket.on('data_updated', function(data) {
    location.reload()
    console.log('Данные обновлены:', data);
});

socket.on('show_modal', function(data) {
    // Обновите страницу с новыми данными
    var modal1P = document.getElementById('modal-text')
    modal1.classList.add("red-color-modal")
    modal1P.textContent = "The account is already being tracked!"
});
