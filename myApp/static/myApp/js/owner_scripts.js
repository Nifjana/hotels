document.addEventListener("DOMContentLoaded", () => {
    const addRoomButton = document.getElementById("addRoomButton");

    if (addRoomButton) {
        addRoomButton.addEventListener("click", addRoomType);
    }

    function addRoomType() {
        const roomTypesContainer = document.getElementById("room-types");

        const roomDiv = document.createElement("div");
        roomDiv.classList.add("room-type");

        roomDiv.innerHTML = `
            <label for="room_type">Room Type:</label>
            <select name="room_type[]" required>
                <option value="single">Single</option>
                <option value="double">Double</option>
                <option value="suite">Suite</option>
            </select><br>

            <label for="room_count">Number of Rooms:</label>
            <input type="number" name="room_count[]" min="1" required><br>

            <label for="facilities">Facilities (comma-separated):</label>
            <input type="text" name="facilities[]" placeholder="WiFi, Parking, Pool"><br>

            <label for="photos">Upload Photos:</label>
            <input type="file" name="photos[]" multiple><br>

            <button type="button" class="remove-room-btn">Remove</button>
        `;

        roomTypesContainer.appendChild(roomDiv);

        const removeBtn = roomDiv.querySelector(".remove-room-btn");
        removeBtn.addEventListener("click", () => {
            roomDiv.remove();
        });
    }
});
