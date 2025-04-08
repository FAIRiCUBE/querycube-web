<template>
  <div class="map-container">
    <div class="coordinates-list">
      <h3>Saved Coordinates</h3>
      <ul>
        <li v-for="(point, index) in savedPoints" :key="index">
          {{ point.name }}
          <button @click="deletePoint(index)">Delete</button>
        </li>
      </ul>
      <button @click="generateCSV">Download Query in CSV format</button>
      <button @click="sendCoordinatesToAPI">Send Coordinates to API</button>
    </div>
    <div id="map" style="height: 500px; width: 100%"></div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default {
  name: "MapComponent",
  emits: ["pointSelected"],
  data() {
    return {
      savedPoints: []
    };
  },
  mounted() {
    // Initialize the map
    this.map = L.map("map").setView([51.505, -0.09], 13);

    // Add OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors"
    }).addTo(this.map);

    // Add click event to the map
    this.map.on("click", (e) => {
      const { lat, lng } = e.latlng;

      // Create a popup
      const popupContent = document.createElement("div");
      const nameInput = document.createElement("input");
      nameInput.type = "text";
      nameInput.placeholder = "Enter name";
      const dateInput = document.createElement("input");
      dateInput.type = "date"; // Changed from datetime-local to date
      const saveButton = document.createElement("button");
      saveButton.textContent = "Save";

      popupContent.appendChild(nameInput);
      popupContent.appendChild(dateInput);
      popupContent.appendChild(saveButton);

      const popup = L.popup().setLatLng([lat, lng]).setContent(popupContent).openOn(this.map);

      saveButton.addEventListener("click", () => {
        const name = nameInput.value;
        const date = dateInput.value.split("T")[0]; // Extract only the date part
        if (name && date) {
          // Ensure both name and date are provided
          this.savedPoints.push({ lat, lng, name, date });
          this.$emit("pointSelected", { lat, lng, name, date });
        } else {
          alert("Please enter a name and select a valid date.");
        }
        this.map.closePopup(popup);
      });
    });
  },
  methods: {
    deletePoint(index) {
      this.savedPoints.splice(index, 1);
    },
    generateCSV() {
      const csvContent = ["sampleId,lat,long,date"];
      this.savedPoints.forEach((point) => {
        const date = point.date ? point.date.split("T")[0] : "";
        csvContent.push(`${point.name},${point.lat},${point.lng},${date}`);
      });
      const blob = new Blob([csvContent.join("\n")], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "coordinates.csv";
      link.click();
      URL.revokeObjectURL(url);
    },
    sendCoordinatesToAPI() {
      const apiUrl = "/api/coordinates"; // Replace with your actual API endpoint
      const payload = this.savedPoints;

      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Failed to send coordinates to the API");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Coordinates successfully sent to the API:", data);
          alert("Coordinates successfully sent to the API");
        })
        .catch((error) => {
          console.error("Error sending coordinates to the API:", error);
          alert("Error sending coordinates to the API");
        });
    }
  },
  beforeUnmount() {
    this.map.remove();
  }
};
</script>

<style>
.map-container {
  position: relative;
}

.coordinates-list {
  position: absolute;
  top: 10px;
  right: 10px; /* Move to the top right */
  background: rgba(255, 255, 255, 0.2); /* Glassmorphism effect */
  backdrop-filter: blur(10px); /* Blur effect */
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.3); /* Subtle border */
}

.coordinates-list h3 {
  margin: 0 0 10px;
  color: #333;
  font-weight: bold;
}

.coordinates-list ul {
  list-style: none;
  padding: 0;
  margin: 0 0 10px;
}

.coordinates-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  color: #333;
}

.coordinates-list button {
  background: #4caf50; /* Green background */
  color: white; /* White text */
  border: none; /* Remove border */
  padding: 1px 2px; /* Smaller padding */
  border-radius: 5px; /* Rounded corners */
  font-size: 0.9em; /* Slightly smaller font size */
  cursor: pointer; /* Pointer cursor on hover */
  transition: background 0.3s, transform 0.2s; /* Smooth transition for hover effects */
}

.coordinates-list button:hover {
  background: #45a049; /* Darker green on hover */
  transform: scale(1.05); /* Slight zoom effect */
}

#map {
  height: 100%;
  width: 100%;
}
</style>
