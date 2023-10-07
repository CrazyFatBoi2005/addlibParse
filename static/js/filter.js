const openFilterBtn = document.getElementById('open-filter');
const closeFilterBtn = document.getElementById('close-filter');
const filterModal = document.getElementById('filter-window');


openFilterBtn.addEventListener('click', () => {
    filterModal.style.display = 'block';
});

closeFilterBtn.addEventListener('click', () => {
    filterModal.style.display = 'none';
});
