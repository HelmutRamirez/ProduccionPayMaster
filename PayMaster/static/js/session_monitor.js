

function filterUsers() {
    const input = document.getElementById('search-input').value.toLowerCase();
    const table = document.getElementById('users-table');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let visible = false;
        for (let j = 0; j < cells.length - 1; j++) {  // Exclude the last cell with the action link
            if (cells[j].textContent.toLowerCase().includes(input)) {
                visible = true;
                break;
            }
        }
        rows[i].style.display = visible ? '' : 'none';
    }
}