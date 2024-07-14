document.addEventListener('DOMContentLoaded', function() {
    // Select all custom-select elements
    const selects = document.querySelectorAll('.custom-select');
  
    selects.forEach(select => {
      const selectItems = select.querySelector('.select-items');
      const selected = select.querySelector('.select-selected');
      const search = select.querySelector('.select-search');
  
      // Click event listener to toggle dropdown
      select.addEventListener('click', function(e) {
        if (e.target.classList.contains('select-selected')) {
          selectItems.classList.toggle('select-hide');
        }
        if (e.target.parentElement.classList.contains('select-items') && !e.target.classList.contains('select-search')) {
          selected.textContent = e.target.textContent;
          selectItems.classList.add('select-hide');
        }
      });
  
      // Input event listener for search
      search.addEventListener('input', function() {
        const filter = search.value.toLowerCase();
        const items = select.querySelectorAll('.select-items div');
        items.forEach(item => {
          if (item.textContent.toLowerCase().includes(filter)) {
            item.style.display = '';
          } else {
            item.style.display = 'none';
          }
        });
      });
  
      // Click outside event listener to close dropdown
      document.addEventListener('click', function(e) {
        if (!select.contains(e.target)) {
          selectItems.classList.add('select-hide');
        }
      });
    });
  });
  