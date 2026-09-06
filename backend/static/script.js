let toastTimer;


function showToast(message) {

    const toast = document.getElementById("toast");

    toast.textContent = message;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);
}


async function loadStatus() {

    try {

        const response = await fetch("/api/status");

        const data = await response.json();


        const databaseStatus =
            document.getElementById("databaseStatus");

        if (data.database) {

            databaseStatus.textContent = "Connected";

            databaseStatus.style.color = "#24a36a";

        } else {

            databaseStatus.textContent = "Offline";

            databaseStatus.style.color = "#e05b5b";

        }


        document.getElementById("backupCount")
            .textContent = data.backup_count;


        if (data.backups.length > 0) {

            document.getElementById("lastBackup")
                .textContent = data.backups[0].timestamp;

        } else {

            document.getElementById("lastBackup")
                .textContent = "None";

        }


        calculateStorage(data.backups);

        loadDemoData();

    } catch (error) {

        console.error(error);

    }
}


async function loadBackups() {

    try {

        const response =
            await fetch("/api/backups");

        const backups =
            await response.json();


        const table =
            document.getElementById("backupTable");


        if (!backups.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="5" class="empty">
                        No backups created yet.
                    </td>
                </tr>
            `;

            return;

        }


        table.innerHTML = backups.map(backup => `

            <tr>

                <td class="filename">
                    ${escapeHtml(backup.filename)}
                </td>

                <td>
                    ${backup.size}
                </td>

                <td>
                    ${backup.timestamp}
                </td>

                <td>
                    <span class="badge">
                        ✓ Local
                    </span>
                </td>

                <td>

                    <button
                        class="restore-btn"
                        onclick="restoreBackup('${escapeHtml(backup.filename)}')">

                        Restore

                    </button>

                </td>

            </tr>

        `).join("");


    } catch (error) {

        console.error(error);

    }
}


async function createBackup() {

    try {

        showToast("Starting backup...");

        const response =
            await fetch("/api/backup", {
                method: "POST"
            });


        const data =
            await response.json();


        showToast(data.message);

        setTimeout(() => {

            loadStatus();
            loadBackups();

        }, 4000);


    } catch (error) {

        showToast("Backup request failed.");

    }
}


async function restoreBackup(filename) {

    const confirmed =
        confirm(
            `Restore database from:\n\n${filename}\n\nThis may overwrite current database data. Continue?`
        );


    if (!confirmed) {
        return;
    }


    try {

        showToast("Starting restore...");


        const response =
            await fetch("/api/restore", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    filename: filename
                })

            });


        const data =
            await response.json();


        showToast(data.message);


    } catch (error) {

        showToast("Restore request failed.");

    }
}


async function addDemoData() {

    try {

        const response =
            await fetch("/api/demo-data", {
                method: "POST"
            });


        const data =
            await response.json();


        showToast(data.message);

        loadDemoData();

    } catch (error) {

        showToast("Could not add demo data.");

    }
}


async function deleteDemoData() {

    const confirmed =
        confirm(
            "This will delete the demo table and simulate data loss. Continue?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch("/api/delete-demo-data", {
                method: "POST"
            });


        const data =
            await response.json();


        showToast(data.message);

        loadDemoData();

    } catch (error) {

        showToast("Could not delete data.");

    }
}


async function loadDemoData() {

    try {

        const response =
            await fetch("/api/demo-data");


        const data =
            await response.json();


        const table =
            document.getElementById("demoTable");


        if (!Array.isArray(data) || data.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="4" class="empty">
                        No demo data found.
                    </td>
                </tr>
            `;

            return;

        }


        table.innerHTML = data.map(row => `

            <tr>

                <td>
                    ${row.id}
                </td>

                <td class="filename">
                    ${escapeHtml(row.name)}
                </td>

                <td>
                    ${escapeHtml(row.course)}
                </td>

                <td>
                    ${row.created_at}
                </td>

            </tr>

        `).join("");


    } catch (error) {

        console.error(error);

    }
}


function calculateStorage(backups) {

    let total = 0;


    backups.forEach(backup => {

        const value =
            parseFloat(backup.size);


        if (backup.size.includes("MB")) {

            total += value * 1024;

        } else if (backup.size.includes("GB")) {

            total += value * 1024 * 1024;

        } else if (backup.size.includes("KB")) {

            total += value;

        } else {

            total += value / 1024;

        }

    });


    if (total > 1024) {

        document.getElementById("storageUsed")
            .textContent =
            (total / 1024).toFixed(1) + " MB";

    } else {

        document.getElementById("storageUsed")
            .textContent =
            total.toFixed(1) + " KB";

    }
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


loadStatus();

loadBackups();

setInterval(() => {

    loadStatus();
    loadBackups();

}, 10000);