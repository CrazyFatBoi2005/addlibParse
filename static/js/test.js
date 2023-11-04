function handleDragStart(e) {
    e.dataTransfer.setData("text/plain", e.target.innerText);
}

function handleDragOver(e) {
    e.preventDefault();
}

function handleDrop(e) {
    e.preventDefault();
    var data = e.dataTransfer.getData("text/plain");
    var droppedElement = document.createElement("li");
    droppedElement.className = "pages-content__content-item";
    droppedElement.innerText = data;
    e.target.appendChild(droppedElement);
}