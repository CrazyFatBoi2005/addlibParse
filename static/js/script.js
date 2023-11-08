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

        setTimeout(function() {
            modal1.classList.remove("show")
            modal1.classList.add("remove")
            setTimeout(function() {
            modal1.classList.remove("remove")
            modal1.classList.add("removed")
    }, 1500);
    }, 5000);

});

closeModalNotif.addEventListener('click', () => {
    modal1.style.display = 'none';
});

var socket = io.connect('http://178.253.42.233:5000');


socket.on('page_changed', function(data) {
    window.location.href = window.location.href;
});

socket.on('show_modal', function(data) {
    var modal1P = document.getElementById('modal-text')
    modal1.classList.add("red-color-modal")
    modal1P.textContent = "The account is already being tracked!"
});


const openGroupModalBtn = document.getElementById('open-group-modal');
const closeGroupModalBtn = document.getElementById('close-group-modal');
const modalGroup = document.getElementById('group-modal-window');


openGroupModalBtn.addEventListener('click', () => {
    modalGroup.style.display = 'block';
});

closeGroupModalBtn.addEventListener('click', () => {
    modalGroup.style.display = 'none';
});


const groupsAddBtn = document.getElementById("options-add-new-group-btn")
groupsAddBtn.addEventListener('click', () => {
    modalGroup.style.display = 'none';
});


const openGroupDeleteModalBtn = document.getElementById('delete-group-btn');
const closeGroupDeleteModalBtn = document.getElementById('close-group-delete-modal');
const modalDeleteGroup = document.getElementById('group-delete-modal-window');

openGroupDeleteModalBtn.addEventListener('click', () => {
    modalDeleteGroup.style.display = 'block';
});

closeGroupDeleteModalBtn.addEventListener('click', () => {
    modalDeleteGroup.style.display = 'none';
});


var openChangeModalBtns = document.querySelectorAll('.edit-channel-btn');
const closeChangeModalBtns = document.querySelectorAll('.close-change-account-group-modal');
const modalChangeGroup = document.getElementById('change-account-group-modal-window');

openChangeModalBtns.forEach(function(button) {
    button.addEventListener('click', function() {
        var accountId = button.getAttribute('data-variable');
        console.log(accountId);
        document.getElementById('accountIdField').value = accountId;
        modalChangeGroup.style.display = 'block';
    });
});

closeChangeModalBtns.forEach(function(button) {
    button.addEventListener('click', function() {
        modalChangeGroup.style.display = 'none';
    });
});


var changeAccountsStatusBtn = document.getElementById('change-accounts-status-btn');
var saveAccountsStatusBtn = document.getElementById('save-accounts-status-btn');
var trackingStatusCheckboxes = document.querySelectorAll('.tracking-status-checkbox');
var changesInvolvedModal = document.getElementById('changes-involved-modal')
var changesSuccessBtn = document.getElementById('changes-success-btn')


var changeAccountsOrderBtn = document.getElementById("change-accounts-order-btn")
var saveAccountsOrderBtn = document.getElementById("save-accounts-order-btn")


changeAccountsStatusBtn.addEventListener('click', () => {
    trackingStatusCheckboxes.forEach(function(trackingStatusCheckbox) {
    trackingStatusCheckbox.disabled = false;
    });
    saveAccountsStatusBtn.style.display = 'flex';
    changeAccountsOrderBtn.disabled = true;
});


saveAccountsStatusBtn.addEventListener('click', () => {
    trackingStatusCheckboxes.forEach(function(trackingStatusCheckbox) {
    trackingStatusCheckbox.disabled = true;
    });
    changeAccountsOrderBtn.disabled = false;

    changesInvolvedModal.style.display = 'block';
    saveAccountsStatusBtn.style.display = 'none';
});

changesSuccessBtn.addEventListener('click', () => {
    changesInvolvedModal.style.display = 'none'
});

function CheckboxStatusHandling(currentGroupId) {
    var currentGroupId = currentGroupId
    var checkboxes = document.querySelectorAll('.tracking-status-checkbox');
    console.log(currentGroupId);
    var statusDict = {};
    checkboxes.forEach(function(checkbox) {
        var checkboxId = checkbox.id
        statusDict[checkboxId] = checkbox.checked;
    });
    statusDict["currentGroupId"] = currentGroupId;
    $.ajax({
        type: 'POST',
        url: '/change_accounts_status',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(statusDict),
        success: function(response) {
            console.log('Успешно отправлено');
        },
        error: function(error) {
            console.error('Ошибка:', error);
        }
    });
}


changeAccountsOrderBtn.addEventListener('click', () => {
    var accountsListElements = document.querySelectorAll(".pages-content__content-item");
    accountsListElements.forEach(function(accountsListEl) {
        accountsListEl.classList.add("pages-content__content-item-ordering")
        accountsListEl.style.cursor = "move";
        accountsListEl.draggable = true;
    });

    saveAccountsOrderBtn.style.display = "flex";
    changeAccountsStatusBtn.disabled = true;
    const accountsList = document.querySelector(".pages-content__content-list");

    accountsList.addEventListener("dragstart", (evt) => {
      evt.target.classList.add("selected");
    })

    accountsList.addEventListener("dragend", (evt) => {
      evt.target.classList.remove("selected");
    });


    accountsList.addEventListener("dragover", (evt) => {
      evt.preventDefault();

      const activeElement = accountsList.querySelector(".selected");
      const currentElement = evt.target;

      const isMoveable = activeElement !== currentElement &&
        currentElement.classList.contains("pages-content__content-item");

      if (!isMoveable) {
        return;
      }

      const nextElement = (currentElement === activeElement.nextElementSibling) ?
          currentElement.nextElementSibling :
          currentElement;

      accountsList.insertBefore(activeElement, nextElement);
    });

});


saveAccountsOrderBtn.addEventListener('click', () => {
    var accountsListElements = document.querySelectorAll(".pages-content__content-item");
    accountsListElements.forEach(function(accountsListEl) {
        accountsListEl.classList.remove("pages-content__content-item-ordering")
        accountsListEl.draggable = false;
    });

    changeAccountsStatusBtn.disabled = false;
    saveAccountsOrderBtn.style.display = "none";

});


function CheckboxOrderHandling(currentGroupId) {
    var accountsListElements = document.querySelectorAll(".pages-content__content-item");
    var currentGroupId = currentGroupId
    var orderList = [];
    accountsListElements.forEach(function(accountsEl) {
        orderList.push(accountsEl.id);
    });
    orderList.push(currentGroupId);
    $.ajax({
        type: 'POST',
        url: '/change_accounts_order',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(orderList),
        success: function(response) {
            console.log('Успешно отправлено');
        },
        error: function(error) {
            console.error('Ошибка:', error);
        }
    });
}
