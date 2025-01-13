import { createApp } from "vue";
import "./assets/index.css";
import App from "./App.vue";
import fetcher from "./fetcher";

import { useToast } from "@/components/ui/toast/use-toast";
const { toast } = useToast();

fetcher.interceptors.error = function (error) {
  console.error(error.error);
  toast({
    description: error.error.message,
  });
  return error;
};

const app = createApp(App);

app.config.errorHandler = (err, vm, info) => {
  console.error(err);
};

app.mount("#app");
