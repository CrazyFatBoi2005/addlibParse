//const tasksListElement = document.querySelector(".pages-content__content-list");
//const taskElements = tasksListElement.querySelectorAll(".pages-content__content-item");
////document.addEventListener('DOMContentLoaded', function() {
////    var tasksList = localStorage.getItem("tasksList");
////    print();
////
////    if (tasksList) {
////        document.querySelector(".pages-content__content-list").innerHTML = tasksList;
////    }
////    for (const task of taskElements) {
////        task.classList.remove("selected");
////    }
////});
//
//var socket = io.connect('http://127.0.0.1:5000');
////localStorage.setItem("tasksList", "");
//
//
//socket.on('page_changed', function(data) {
//    location.reload();
//});
//
//
//for (const task of taskElements) {
//  task.draggable = true;
//}
//
//
//tasksListElement.addEventListener("dragstart", (evt) => {
//  evt.target.classList.add("selected");
//})
//
//tasksListElement.addEventListener("dragend", (evt) => {
//  evt.target.classList.remove("selected");
//});
//
//
//tasksListElement.addEventListener("dragover", (evt) => {
//  evt.preventDefault();
//
//  const activeElement = tasksListElement.querySelector(".selected");
//  const currentElement = evt.target;
//
//  const isMoveable = activeElement !== currentElement &&
//    currentElement.classList.contains("pages-content__content-item");
//
//  if (!isMoveable) {
//    return;
//  }
//
//  const nextElement = (currentElement === activeElement.nextElementSibling) ?
//      currentElement.nextElementSibling :
//      currentElement;
//
//  tasksListElement.insertBefore(activeElement, nextElement);
//  var tasksList = document.querySelector(".pages-content__content-list").innerHTML;
//  localStorage.setItem("tasksList", tasksList);
//  var tasksListElementCh = document.querySelector(".pages-content__content-list");
//  var taskElementsCh = tasksListElement.querySelectorAll(".pages-content__content-item");
//  var idList = [];
//
//  taskElementsCh.forEach(function(element) {
//       var id = element.id;
//       idList.push(id);
//  })
//  $.ajax({
//      url: 'http://127.0.0.1:5000/receive_html',
//      type: 'POST',
//      contentType: 'application/json;charset=UTF-8',
//      data: JSON.stringify({'id_list': idList}),
//      success: function(response) {
//          console.log('Список успешно отправлен на сервер');
//      }
//  });
//});
