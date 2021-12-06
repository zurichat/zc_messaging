import React from "react"
import { Switch, Route, Redirect } from "react-router-dom"
import { ChannelBrowser, DmBrowser, MessagingBoard, Threads } from "../pages"

/**
 * Main Routing for the zc messaging plugin.
 * All other routing must somehow be a descendant of this component.
 */
const Routes = () => (
  <Switch>
    <Route path="/" exact component={MessagingBoard} />
    <Route path="/browse-channels" component={ChannelBrowser} />
    <Route path="/threads" component={Threads} />
    <Route path="/all-dms" component={DmBrowser} />
    <Route path="/:roomId" component={MessagingBoard} />
    {/* <Route exact path="*">
      <Redirect to="/all-dms" />
    </Route> */}
  </Switch>
)

export default Routes
