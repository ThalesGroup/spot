import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "en-US",
  title: "spot",
  description: "Satellite Mission Planning with Rydberg Atoms",

  theme,

  // Enable it with pwa
  // shouldPrefetch: false,
});
