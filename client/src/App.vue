<script setup>
import { ref, onMounted } from "vue";
import IconAdd from "~icons/material-symbols/add-circle-outline";
import IconError from "~icons/clarity/error-standard-solid";
import IconLoading from "~icons/mingcute/loading-fill";
import IconDownload from "~icons/material-symbols/download-2-rounded";
import IconWeb from "~icons/mdi/web";
import IconSpinner from "~icons/svg-spinners/3-dots-rotate";
import IconGithub from "~icons/mdi/github";
import IconHelp from "~icons/ic/twotone-help";
import fetcher from "./lib/fetcher";
import reader from "./lib/reader";
import Popup from "./components/Popup.vue";
import MapComponent from "./components/Map.vue";

var file = ref(null);
var dragging = ref(false);
var loading = ref(false);
var error = ref(null);
var showPopup = ref(false);
var showConfirm = ref(false);

let datagrid = null;
let logGrid = null;
let layerInfo = null;

onMounted(async () => {
  console.log("Hello QueryCube");
  datagrid = initGrid("#dataGrid");
  logGrid = initGrid("#logGrid");
});

const initGrid = (name) => {
  const gridOptions = {
    autoSizeStrategy: { type: "fitCellContents" },
    domLayout: "autoHeight",
    rowData: [],
    columnDefs: []
  };

  const myGridElement = document.querySelector(name);
  return agGrid.createGrid(myGridElement, gridOptions);
};

const loadGrid = (grid, data) => {
  if (!data.length) return;
  grid.setGridOption(
    "columnDefs",
    Object.keys(data[0]).map((key) => ({
      headerName: key,
      field: key,
      sortable: true,
      filter: true,
      resizable: true
    }))
  );
  grid.setGridOption("rowData", data);
};

const downloadGrid = (grid, filename) => {
  const params = {
    fileName: filename
    // exportedRows: "all"
  };
  grid.exportDataAsCsv(params);
};

const showConfirmPopup = async (e) => {
  showConfirm.value = true;
};

const onFileChange = async (e) => {
  console.log("File changed");

  if (!file.value.files.length) return;
  var f = file.value.files[0];
  reset();

  console.log(f);

  if (!(await verifyFile(f))) return;
  loading.value = true;

  const formData = new FormData();
  formData.append("file", f, f.name);
  formData.append("layer_info", layerInfo);

  const get = await fetcher.upload("api/querycube", formData);
  console.log(get.data);

  if (get.isError) {
    console.error(get.error);
    error.value = get.error.message;
    loading.value = false;
    return;
  }

  loadGrids(get.data);

  loading.value = false;
};

const verifyFile = async (file) => {
  try {
    if (!file) return false;
    if (file.type !== "text/csv") {
      error.value = "Invalid file type. Please upload a CSV file";
      return false;
    }
    // check if the first row of the filecontent contains the correct headers
    var content = await reader.read(file);
    const firstRow = content.split("\n")[0];
    const headers = firstRow.split(",");
    const expectedHeaders = ["sampleid", "lat", "long"];
    const hasHeaders = expectedHeaders.every((header) => headers.map((h) => h.trim().toLowerCase()).includes(header.toLowerCase()));

    console.log(headers, expectedHeaders, hasHeaders);

    if (!hasHeaders) {
      error.value = "Invalid file content. Please make sure the file contains sampleid, lat, long headers";
      return false;
    }
    return true;
  } catch (error) {
    console.error(error);
    error.value = "An error occurred while verifying the file";
    return false;
  }
};

const loadGrids = async (data) => {
  loadGrid(datagrid, data.result);
  loadGrid(logGrid, data.log);
};

const onFileDragover = (e) => {
  e.preventDefault();
  dragging.value = true;
};

const onFileDragleave = (e) => {
  e.preventDefault();
  dragging.value = false;
};

const onFileDrop = (e) => {
  e.preventDefault();
  file.value.files = e.dataTransfer.files;
  showConfirm.value = true;
  dragging.value = false;
};

const reset = () => {
  datagrid.setGridOption("rowData", []);
  datagrid.setGridOption("columnDefs", []);
  logGrid.setGridOption("rowData", []);
  logGrid.setGridOption("columnDefs", []);
  file.value.value = "";
  file.value = null;
  error.value = null;
};

const handlePointSelected = (point) => {
  console.log("Point selected:", point);
};
</script>

<template>
  <popup :show="showConfirm" title="Is this the file you want to upload?">
    <div class="flex flex-col gap-2">
      <div class="flex gap-1">
        <div class="font-bold">File:</div>
        <div class="flex-1 truncate">{{ file ? file.files[0].name : "" }}</div>
      </div>
      <div class="flex gap-1">
        <div class="font-bold">Size:</div>
        <div class="flex-1 truncate">{{ file ? file.files[0].size : "" }}</div>
      </div>
      <div class="flex gap-1 mb-2">
        <div class="font-bold">Type:</div>
        <div class="flex-1 truncate">{{ file ? file.files[0].type : "" }}</div>
      </div>
      <div class="border-b"></div>
      <div class="flex gap-2 mt-2">
        <button
          class="btn btn-primary"
          @click="
            showConfirm = false;
            reset();
          "
        >
          No
        </button>
        <button
          class="btn btn-primary"
          @click="
            showConfirm = false;
            onFileChange();
          "
        >
          Yes
        </button>
      </div>
    </div>
  </popup>
  <popup :show="showPopup" title="Documentation" @on-close="showPopup = false">
    <div class="flex flex-col gap-2">
      <div class="flex flex-col">
        <div class="font-bold">Requirements for the file to upload</div>
        <div class="px-2">- It must be a csv file</div>
        <div class="px-2">
          - The file must include the headers
          <span class="italic">sampleid, lat, long</span>
        </div>
        <div class="px-2">
          - The header
          <span class="italic">date</span>
          is optional
        </div>
        <div class="px-2 text-blue-600">
          -
          <a href="samplesfile.csv" class="hover:text-teal-600">Download a samplefile</a>
        </div>
      </div>
      <div class="flex flex-col">
        <div class="font-bold">Layers</div>
        <div class="px-2 text-blue-600">
          -
          <a href="https://fairicube.rasdaman.com/rasdaman/ows#/services" class="hover:text-teal-600" target="_blank">See available layers here</a>
        </div>
      </div>
    </div>
  </popup>

  <!-- TOP SECTION -->
  <div class="top-section relative w-full h-[60vh]">
    <MapComponent class="absolute inset-0 z-0" @pointSelected="handlePointSelected" />
    <div class="absolute top-0 left-0 right-0 z-10 flex flex-col items-center pointer-events-none">
      <!-- LOGO AND OPTIONS CONTAINER -->
      <div class="glassmorphism-container w-full max-w-[500px] mt-4 p-4 rounded-lg pointer-events-auto">
        <!-- LOGO -->
        <div class="flex flex-col items-center">
          <img src="/fairicube_logo.png" class="w-20" />
          <div class="font-semibold text-lg">QueryCube</div>
          <div class="flex gap-2 text-lg">
            <a href="https://fairicube.nilu.no/"><icon-web class="text-[#5e81ac] hover:text-teal-600 hover:cursor-pointer" /></a>
            <a href="https://github.com/FAIRiCUBE/uc3-drosophola-genetics/tree/main/projects/QueryCube"><icon-github class="text-[#b48ead] hover:text-teal-600 hover:cursor-pointer" /></a>
          </div>
        </div>

        <!-- OPTIONS -->
        <div class="flex flex-col items-center gap-2 mt-4">
          <div class="rounded border-2 border-dashed bg-white p-6 flex flex-col items-center gap-2 hover:cursor-pointer hover:border-teal-600" :class="[dragging ? 'border-teal-600 ' : 'border-gray-400 ']" @dragover="onFileDragover" @dragleave="onFileDragleave" @drop="onFileDrop" @click="$refs.file.click()">
            <div>
              <icon-add class="text-xl" v-if="!loading" />
              <icon-loading class="text-2xl animate-spin" v-else />
            </div>
            <div class="text-center">
              <span v-if="!loading">Drag and drop it like it's hot, or click to upload file and generate data</span>
              <span v-else>
                <b>Loading...</b>
                <br />
                This may take a while...
              </span>
            </div>
            <input type="file" class="hidden" accept=".csv" ref="file" @change="showConfirm = true" />
          </div>
          <div class="flex cursor-pointer gap-1 hover:text-blue-600 text-gray-700" @click="showPopup = true">
            <icon-help class="self-center" />
            <div class="self-center">Documentation</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- BOTTOM SECTION -->
  <div class="bottom-section w-full p-6">
    <!-- RESULTS -->
    <div class="w-full flex flex-col">
      <div class="flex gap-2">
        <div class="font-bold self-center">Result</div>
        <icon-download class="self-center text-[#d08770] hover:text-teal-600 hover:cursor-pointer" @click="downloadGrid(datagrid, 'querycube_result.csv')" />
      </div>
      <div id="dataGrid" class="w-full"></div>
    </div>

    <!-- LOG -->
    <div class="w-full flex flex-col mt-6">
      <div class="flex gap-2">
        <div class="font-bold self-center">Log</div>
        <icon-download class="self-center text-[#d08770] hover:text-teal-600 hover:cursor-pointer" @click="downloadGrid(logGrid, 'querycube_log.csv')" />
      </div>
      <div id="logGrid" class="w-full"></div>
    </div>
  </div>
</template>

<style>
html,
body {
  @apply h-full w-full text-[17px] m-0;
}

body {
  @apply h-full font-sans antialiased;
  background-color: #ededeb;
}

#app {
  @apply flex flex-col min-h-full items-stretch relative flex-1 w-full h-full gap-6;
}

.top-section {
  @apply relative;
}

.bottom-section {
  @apply bg-white;
}

.glassmorphism-container {
  @apply bg-white/30 backdrop-blur-md shadow-md;
}

.pointer-events-none {
  pointer-events: none;
}

.pointer-events-auto {
  pointer-events: auto;
}

.btn {
  @apply border border-gray-300 rounded px-4 py-1 text-sm font-semibold hover:bg-gray-100;
}
</style>
