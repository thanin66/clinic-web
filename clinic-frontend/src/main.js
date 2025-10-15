// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// ✅ Import Vuetify core
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// ✅ สร้าง instance ของ Vuetify
const vuetify = createVuetify({
    components,
    directives,
});

// ✅ สร้าง Vue app
const app = createApp(App);

// ✅ ติดตั้ง plugin ต่าง ๆ
app.use(router);
app.use(vuetify);

// ✅ mount
app.mount("#app");
