<script setup>
import { ref, onMounted } from "vue";
import IconAdd from "~icons/material-symbols/add-circle-outline";
import IconError from "~icons/clarity/error-standard-solid";
import IconLoading from "~icons/mingcute/loading-fill";
import IconDownload from "~icons/material-symbols/download-2-rounded";
import IconWeb from "~icons/mdi/web";
import IconGithub from "~icons/mdi/github";
import fetcher from "./lib/fetcher";

var file = ref(null);
var dragging = ref(false);
var loading = ref(false);
var error = ref(null);

let datagrid = null;
let logGrid = null;

onMounted(async () => {
  console.log("Hoi");

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

const onFileChange = async (e) => {
  if (!file.value.files.length) return;
  var f = file.value.files[0];
  reset();
  loading.value = true;

  const formData = new FormData();
  formData.append("file", f, f.name);
  const get = await fetcher.upload("api/wormpicker", formData);
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
  onFileChange();
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
</script>

<template>
  <!-- LOGO -->
  <div class="flex flex-col self-center">
    <img src="/fairicube_logo.png" class="w-20 self-center" />
    <div class="self-center font-semibold text-lg">Wormpicker</div>
    <div class="flex gap-2 self-center text-lg">
      <a href="https://fairicube.nilu.no/"><icon-web class="self-center text-[#5e81ac] hover:text-teal-600 hover:cursor-pointer" /></a>
      <a href="https://github.com/FAIRiCUBE/uc3-drosophola-genetics/tree/main/projects/WormPickerOOP"><icon-github class="self-center text-[#b48ead] hover:text-teal-600 hover:cursor-pointer" /></a>
    </div>
  </div>

  <!-- OPTIONS -->
  <div class="self-center flex">
    <div class="rounded border-2 border-dashed md:w-[800px] bg-white p-6 flex flex-col items-center gap-2 hover:cursor-pointer hover:border-teal-600" :class="[dragging ? 'border-teal-600 ' : 'border-gray-400 ']" @dragover="onFileDragover" @dragleave="onFileDragleave" @drop="onFileDrop" @click="$refs.file.click()">
      <div>
        <icon-add class="text-xl" v-if="!loading" />
        <icon-loading class="text-2xl animate-spin" v-else />
      </div>
      <div class="text-center">
        <span v-if="!loading">Drag and drop or click to upload file and generate data</span>
        <span v-else>
          <b>Loading...</b>
          <br />
          This may take a while...
        </span>
      </div>
      <!-- <div class="text-sm font-bold">Max file size: 10 MB</div> -->
      <input type="file" class="hidden" accept=".csv" ref="file" @change="onFileChange" />
    </div>
  </div>

  <!-- ERROR -->
  <div v-if="error" class="flex flex-col self-center md:w-[800px] border border-gray-300 rounded bg-white p-2 gap-2">
    <div class="flex gap-2">
      <div class="self-center">
        <icon-error class="text-red-500" />
      </div>
      <div class="self-center flex-1">{{ error }}</div>
    </div>
  </div>

  <!-- RESULTS -->
  <div class="w-full flex flex-col">
    <div class="flex gap-2">
      <div class="font-bold self-center">Result</div>
      <icon-download class="self-center text-[#d08770] hover:text-teal-600 hover:cursor-pointer" @click="downloadGrid(datagrid, 'wormpicker_result.csv')" />
    </div>
    <div id="dataGrid" class="w-full"></div>
  </div>

  <!-- LOG -->
  <div class="w-full flex flex-col">
    <div class="flex gap-2">
      <div class="font-bold self-center">Log</div>
      <icon-download class="self-center text-[#d08770] hover:text-teal-600 hover:cursor-pointer" @click="downloadGrid(logGrid, 'wormpicker_log.csv')" />
    </div>
    <div id="logGrid" class="w-full"></div>
  </div>
</template>

<style>
html,
body {
  @apply h-full w-full text-[17px];
}

body {
  @apply h-full font-sans antialiased m-0;
  background-color: #ededeb;
}

#app {
  @apply flex flex-col min-h-full items-stretch relative flex-1 w-full h-full p-6 gap-6;
}
</style>
