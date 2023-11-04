const tasksListElement = document.querySelector(".pages-content__content-list");
const taskElements = tasksListElement.querySelectorAll(".pages-content__content-item");


document.addEventListener('DOMContentLoaded', function() {

    var tasksList = localStorage.getItem("tasksList");
    if (tasksList) {
        document.querySelector(".pages-content__content-list").innerHTML = tasksList;
    }
});

for (const task of taskElements) {
  task.draggable = true;
}


tasksListElement.addEventListener("dragstart", (evt) => {
  evt.target.classList.add("selected");
})

tasksListElement.addEventListener("dragend", (evt) => {
  evt.target.classList.remove("selected");
});


tasksListElement.addEventListener("dragover", (evt) => {
  evt.preventDefault();

  const activeElement = tasksListElement.querySelector(".selected");
  const currentElement = evt.target;
  const isMoveable = activeElement !== currentElement &&
    currentElement.classList.contains("pages-content__content-item");

  if (!isMoveable) {
    return;
  }

  const nextElement = getNextElement(evt.clientY, currentElement);

  if (
    nextElement &&
    activeElement === nextElement.previousElementSibling ||
    activeElement === nextElement
  ) {
    return;
  }

  tasksListElement.insertBefore(activeElement, nextElement);
  var tasksList = document.querySelector(".pages-content__content-list").innerHTML;
  localStorage.setItem("tasksList", tasksList);
});



const getNextElement = (cursorPosition, currentElement) => {
  const currentElementCoord = currentElement.getBoundingClientRect();
  const currentElementCenter = currentElementCoord.y + currentElementCoord.height / 2;

  const nextElement = (cursorPosition < currentElementCenter) ?
      currentElement :
      currentElement.nextElementSibling;

  return nextElement;
};