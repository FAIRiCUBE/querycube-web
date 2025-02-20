<script setup>
import IconClose from "~icons/uil/times";

const emit = defineEmits(["on-close"]);

const props = defineProps({
  show: Boolean,
  title: String
});

const onClose = () => {
  emit("on-close");
};
</script>

<template>
  <div class="absolute top-0 bottom-0 left-0 right-0 bg-black bg-opacity-30 z-[100]" @click.self="onClose" v-if="show">
    <div class="absolute top-1/3 left-1/2 p-4 border border-nord4 rounded-xl flex flex-col gap-2 bg-gray-50 shadow z-[110] -translate-x-1/2 -translate-y-1/2 min-w-96 text-sm">
      <div class="select-none font-bold flex justify-between">
        <div>{{ title }}</div>
        <icon-close class="self-center text-nord3 hover:cursor-pointer hover:text-nord0" @click="onClose" />
      </div>
      <div class="border border-gray-300"></div>
      <div><slot></slot></div>
    </div>
  </div>
</template>
