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
        <button @click="generateCSV" aria-label="Download CSV" title="Download a CSV file of the selected positions">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="m17 17.2l-.9-.9q-.275-.275-.7-.275t-.7.275t-.275.7t.275.7l2.6 2.6q.3.3.7.3t.7-.3l2.6-2.6q.275-.275.275-.7t-.275-.7t-.7-.275t-.7.275l-.9.9v-3.175q0-.425-.288-.712T18 13.025t-.712.288t-.288.712zM15 22h6q.425 0 .713.288T22 23t-.288.713T21 24h-6q-.425 0-.712-.288T14 23t.288-.712T15 22m-9-2q-.825 0-1.412-.587T4 18V4q0-.825.588-1.412T6 2h6.175q.4 0 .763.15t.637.425l4.85 4.85q.275.275.425.638t.15.762v1.2q0 .425-.288.712t-.712.288t-.712-.288t-.288-.712V9h-3.5q-.625 0-1.062-.437T12 7.5V4H6v14h5q.425 0 .713.288T12 19t-.288.713T11 20zm0-2V4z" />
          </svg>
        </button>
<!--         <button @click="sendCoordinatesToAPI" aria-label="Send to API" title="Send the current list of positions to the API">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="M6 20q-.825 0-1.412-.587T4 18v-2q0-.425.288-.712T5 15t.713.288T6 16v2h12v-2q0-.425.288-.712T19 15t.713.288T20 16v2q0 .825-.587 1.413T18 20zm5-12.15L9.125 9.725q-.3.3-.712.288T7.7 9.7q-.275-.3-.288-.7t.288-.7l3.6-3.6q.15-.15.325-.212T12 4.425t.375.063t.325.212l3.6 3.6q.3.3.288.7t-.288.7q-.3.3-.712.313t-.713-.288L13 7.85V15q0 .425-.288.713T12 16t-.712-.288T11 15z" />
          </svg>
        </button> -->
        <button @click="switchToDefaultMap" :class="{ active: currentLayerType === 'default' }" aria-label="Default Map" title="Switch to the default map layer">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="m12 21.05l-9-7l1.65-1.25L12 18.5l7.35-5.7L21 14.05zM12 16L3 9l9-7l9 7zm0-2.55L17.75 9L12 4.55L6.25 9z" />
          </svg>
        </button>
        <button @click="switchToTopoMap" :class="{ active: currentLayerType === 'topo' }" aria-label="Topo Map" title="Switch to the topographic map layer">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="m12 21.05l-9-7l1.65-1.25L12 18.5l7.35-5.7L21 14.05zM12 16L3 9l9-7l9 7z" />
          </svg>
        </button>
      </div>
    </div>
    <div id="map" class="fullscreen-map"></div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import fetcher from "./../lib/fetcher"; // Import fetcher

// Set custom marker icon
const customIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28]
});

export default {
  name: "MapComponent",
  emits: ["pointSelected"],
  data() {
    return {
      savedPoints: [],
      mapMarkers: [], // Track markers on the map
      currentLayer: null, // Track the current map layer
      currentLayerType: "default" // Track the current map type
    };
  },
  mounted() {
    // Initialize the map
    this.map = L.map("map", {
      crs: L.CRS.EPSG3857 // Ensure the map uses the correct projection
    }).setView([48.2052, 16.3539], 5);

    // Add default map tiles
    this.currentLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 22,
      attribution: "© OpenStreetMap contributors"
    }).addTo(this.map);

    // Add a predefined sample location marker
    const predefinedSample = {
      lat: 48.2052423,
      lng: 16.35974656,
      name: "Sample_Location",
      date: "1891-01-01"
    };

    this.savedPoints.push(predefinedSample);

    const marker = L.marker([predefinedSample.lat, predefinedSample.lng], { icon: customIcon }).addTo(this.map);
    marker.bindTooltip(`Coordinates: ${predefinedSample.lat}, ${predefinedSample.lng} | Date: ${predefinedSample.date}`, {
      permanent: false,
      direction: "top"
    });
    this.mapMarkers.push(marker);


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
          const marker = L.marker([roundedLat, roundedLng], { icon: customIcon }).addTo(this.map);
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
        maxZoom: 22,
        attribution: "© OpenStreetMap contributors"
      }).addTo(this.map);
      this.currentLayerType = "default"; // Update the current map type
    },
    switchToTopoMap() {
      if (this.currentLayer) this.map.removeLayer(this.currentLayer);
      this.currentLayer = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        maxZoom: 22,
        attribution: "© OpenStreetMap contributors, © OpenTopoMap"
      }).addTo(this.map);
      this.currentLayerType = "topo"; // Update the current map type
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
  @apply absolute top-10 right-10 bg-white bg-opacity-60 backdrop-blur-md p-4 rounded-lg shadow z-10 border border-white/30 grid gap-2;
}

.coordinates-list h3 {
  @apply m-0 text-gray-700 font-semibold text-center text-sm;
}

.coordinates-list ul {
  @apply list-none p-0 m-0 overflow-y-auto max-h-48;
}

.coordinate-item {
  @apply flex justify-between items-center py-1 border-b  text-xs;
}

.coordinate-item::after {
  opacity: 0;
  pointer-events: none;
}

.actions {
  @apply flex gap-1;
}

.icon {
  @apply w-4 h-4 cursor-pointer transition-transform;
}

.icon:hover {
  @apply scale-110;
}

.button-group {
  @apply flex justify-around gap-2;
}

.button-group button {
  @apply p-1 rounded transition-transform;
}

.button-group button.active {
  @apply bg-blue-500 text-white scale-110;
}

.button-group button:hover {
  @apply scale-110;
}

.fullscreen-map {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
}
</style>
