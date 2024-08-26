function showMutations(details) {
    var topRightPanel = document.getElementById("top-right-panel-content");
    topRightPanel.innerHTML = details;
}

function updateNotes(mutant_index, note) {
    // Get the current URL
    const urlParams = new URLSearchParams(window.location.search);
    // Extract the 'file' parameter from the URL
    const file = urlParams.get('file') || 'mutation_report.csv';
    console.log('file:', file);
    fetch('/update_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `mutant_index=${mutant_index}&note=${encodeURIComponent(note)}&file=${encodeURIComponent(file)}`
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function sortTable(columnIndex) {
    var table, rows, switching, i, x, y, shouldSwitch, direction, switchcount = 0;
    table = document.getElementById("fileTable");
    switching = true;
    direction = "asc"; // Set the sorting direction to ascending

    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[columnIndex];
            y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
            if (direction == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (direction == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount ++;
        } else {
            if (switchcount == 0 && direction == "asc") {
                direction = "desc";
                switching = true;
            }
        }
    }
}
