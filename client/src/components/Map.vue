<template>
  <div class="map-container">
    <div class="coordinates-list">
      <h3>Saved Coordinates</h3>
      <ul>
        <li v-for="(point, index) in savedPoints" :key="index" class="coordinate-item" :title="`Coordinates: ${point.lat}, ${point.lng} | Date: ${point.date}`">
          <span>{{ point.name }}</span>
          <div class="actions">
            <button @click="deletePoint(index)" aria-label="Delete">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </li>
      </ul>
      <div class="button-group">
        <button @click="generateCSV" aria-label="Download CSV">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="m17 17.2l-.9-.9q-.275-.275-.7-.275t-.7.275t-.275.7t.275.7l2.6 2.6q.3.3.7.3t.7-.3l2.6-2.6q.275-.275.275-.7t-.275-.7t-.7-.275t-.7.275l-.9.9v-3.175q0-.425-.288-.712T18 13.025t-.712.288t-.288.712zM15 22h6q.425 0 .713.288T22 23t-.288.713T21 24h-6q-.425 0-.712-.288T14 23t.288-.712T15 22m-9-2q-.825 0-1.412-.587T4 18V4q0-.825.588-1.412T6 2h6.175q.4 0 .763.15t.637.425l4.85 4.85q.275.275.425.638t.15.762v1.2q0 .425-.288.712t-.712.288t-.712-.288t-.288-.712V9h-3.5q-.625 0-1.062-.437T12 7.5V4H6v14h5q.425 0 .713.288T12 19t-.288.713T11 20zm0-2V4z" /></svg>
        </button>
        <button @click="sendCoordinatesToAPI" aria-label="Send to API">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M6 20q-.825 0-1.412-.587T4 18v-2q0-.425.288-.712T5 15t.713.288T6 16v2h12v-2q0-.425.288-.712T19 15t.713.288T20 16v2q0 .825-.587 1.413T18 20zm5-12.15L9.125 9.725q-.3.3-.712.288T7.7 9.7q-.275-.3-.288-.7t.288-.7l3.6-3.6q.15-.15.325-.212T12 4.425t.375.063t.325.212l3.6 3.6q.3.3.288.7t-.288.7q-.3.3-.712.313t-.713-.288L13 7.85V15q0 .425-.288.713T12 16t-.712-.288T11 15z" /></svg>
        </button>
      </div>
      <div class="button-group">
        <button @click="switchToDefaultMap">Default Map</button>
        <button @click="switchToTopoMap">Topo Map</button>
      </div>
    </div>
    <div id="map" class="fullscreen-map"></div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import fetcher from "./../lib/fetcher"; // Import fetcher

export default {
  name: "MapComponent",
  emits: ["pointSelected"],
  data() {
    return {
      savedPoints: [],
      mapMarkers: [], // Track markers on the map
      currentLayer: null // Track the current map layer
    };
  },
  mounted() {
    // Initialize the map
    this.map = L.map("map").setView([48.2052, 16.3599], 16); // Correct coordinates for the Natural History Museum in Vienna, Austria

    // Add default map tiles
    this.currentLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
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
          const roundedLat = parseFloat(lat.toFixed(Math.min(8, lat.toString().split(".")[1]?.length || 0))); // Max 8 decimal places
          const roundedLng = parseFloat(lng.toFixed(Math.min(8, lng.toString().split(".")[1]?.length || 0))); // Max 8 decimal places
          this.savedPoints.push({ lat: roundedLat, lng: roundedLng, name, date });
          this.$emit("pointSelected", { lat: roundedLat, lng: roundedLng, name, date });

          // Add a marker to the map
          const marker = L.marker([roundedLat, roundedLng]).addTo(this.map);
          marker.bindTooltip(`Coordinates: ${roundedLat}, ${roundedLng} | Date: ${date}`, {
            permanent: false,
            direction: "top"
          });
          this.mapMarkers.push(marker);
        } else {
          alert("Please enter a name and select a valid date.");
        }
        this.map.closePopup(popup);
      });
    });
  },
  methods: {
    switchToDefaultMap() {
      if (this.currentLayer) this.map.removeLayer(this.currentLayer);
      this.currentLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors"
      }).addTo(this.map);
    },
    switchToTopoMap() {
      if (this.currentLayer) this.map.removeLayer(this.currentLayer);
      this.currentLayer = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        maxZoom: 17,
        attribution: "© OpenStreetMap contributors, © OpenTopoMap"
      }).addTo(this.map);
    },
    deletePoint(index) {
      const point = this.savedPoints[index];
      this.savedPoints.splice(index, 1);

      // Find and remove the marker associated with the deleted point
      const markerToRemove = this.mapMarkers.find((marker) => {
        const markerLatLng = marker.getLatLng();
        return markerLatLng.lat === point.lat && markerLatLng.lng === point.lng;
      });

      if (markerToRemove) {
        this.map.removeLayer(markerToRemove);
        this.mapMarkers = this.mapMarkers.filter((marker) => marker !== markerToRemove);
      }
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
    async sendCoordinatesToAPI() {
      // Generate CSV content
      const csvContent = ["sampleId,lat,long,date"];
      this.savedPoints.forEach((point) => {
        const date = point.date ? point.date.split("T")[0] : "";
        csvContent.push(`${point.name},${point.lat},${point.lng},${date}`);
        console.log(`Point: ${point.name}, Lat: ${point.lat}, Lng: ${point.lng}, Date: ${date}`);
      });

      // Create a Blob for the CSV file
      const blob = new Blob([csvContent.join("\n")], { type: "text/csv" });
      const file = new File([blob], "coordinates.csv", { type: "text/csv" });

      // Log the file for debugging
      console.log("Generated CSV file:", file);

      // Prepare FormData
      const formData = new FormData();
      formData.append("file", file, file.name);
      formData.append("layer_info", "layerInfoPlaceholder"); // Replace with actual layer info if needed

      // Log the request payload for debugging
      console.log("Request payload (FormData):");
      console.log(formData);
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
      }

      // Send the FormData to the API
      try {
        const response = await fetcher.upload("api/querycube", formData);
        console.log(response.data);

        if (response.isError) {
          console.error(response.error);
          alert(`Error: ${response.error.message}`);
          return;
        }

        // Handle successful response
        alert("Coordinates successfully sent to the API.");
      } catch (error) {
        console.error("Error sending coordinates to API:", error);
        alert("An error occurred while sending coordinates to the API.");
      }
    }
  },
  beforeUnmount() {
    this.map.remove();
  }
};
</script>

<style>
@import "tailwindcss/tailwind.css";

.map-container {
  position: relative;
}

.coordinates-list {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(3px);
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 10px;
}

.coordinates-list h3 {
  margin: 0;
  color: #333;
  font-weight: bold;
  text-align: center;
}

.coordinates-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  max-height: 200px;
}

.coordinate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.coordinate-item:hover::after {
  content: attr(title);
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 5px 10px;
  border-radius: 5px;
  white-space: nowrap;
  z-index: 10;
  opacity: 1;
  transition: none; /* Removed delay */
}

.coordinate-item::after {
  opacity: 0;
  pointer-events: none;
}

.actions {
  display: flex;
  gap: 5px;
}

.icon {
  width: 20px;
  height: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.icon:hover {
  transform: scale(1.1);
}

.button-group {
  display: flex;
  justify-content: space-around;
  gap: 10px;
}

.fullscreen-map {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
}
</style>
