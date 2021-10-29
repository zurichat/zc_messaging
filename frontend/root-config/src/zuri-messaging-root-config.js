import { registerApplication, start } from "single-spa"

registerApplication({
  name: "@zuri/messaging",
  app: () => System.import("@zuri/messaging"),
  activeWhen: ["/"]
})

start({
  urlRerouteOnly: true
})
