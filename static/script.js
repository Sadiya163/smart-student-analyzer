const container = document.getElementById("subjects");
const addButton = document.getElementById("addSubject");

if (container && addButton) {
    addButton.addEventListener("click", () => {
        const row = document.createElement("div");
        row.className = "subject-row";
        row.innerHTML = `
            <input type="text" name="subject[]" placeholder="Subject name" required>
            <input type="number" name="score[]" placeholder="Marks" min="0" max="100" step="0.01" required>
            <button type="button" class="remove-btn">×</button>
        `;
        container.appendChild(row);
    });

    container.addEventListener("click", (event) => {
        if (!event.target.classList.contains("remove-btn")) return;

        const rows = container.querySelectorAll(".subject-row");
        if (rows.length > 1) {
            event.target.closest(".subject-row").remove();
        } else {
            alert("At least one subject is required.");
        }
    });
}
