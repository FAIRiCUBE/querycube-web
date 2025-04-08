<template>
  <div id="map" style="height: 500px; width: 100%"></div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default {
  name: "MapComponent",
  emits: ["pointSelected"],
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
      dateInput.type = "datetime-local";
      const saveButton = document.createElement("button");
      saveButton.textContent = "Save";

      popupContent.appendChild(nameInput);
      popupContent.appendChild(dateInput);
      popupContent.appendChild(saveButton);

      const popup = L.popup().setLatLng([lat, lng]).setContent(popupContent).openOn(this.map);

      saveButton.addEventListener("click", () => {
        const name = nameInput.value;
        const date = dateInput.value;
        this.$emit("pointSelected", { lat, lng, name, date });
        this.map.closePopup(popup);
      });
    });
  },
  beforeUnmount() {
    this.map.remove();
  }
};
</script>

<style>
#map {
  height: 100%;
  width: 100%;
}
</style>
