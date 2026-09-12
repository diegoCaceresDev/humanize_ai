import { defineConfig } from "wxt";

export default defineConfig({
  modules: ["@wxt-dev/module-react"],
  manifest: {
    name: "Humanize AI",
    description: "Turn any open webpage into a grounded UX review.",
    version: "0.1.0",
    permissions: ["activeTab", "scripting", "storage"],
    host_permissions: [
      "http://localhost:8000/*",
      "https://*.onrender.com/*"
    ],
    action: {
      default_title: "Humanize this page"
    }
  }
});
