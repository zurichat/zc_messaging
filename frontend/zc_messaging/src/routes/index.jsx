import React from "react"
import {
  Switch,
  Route,
  BrowserRouter as Router,
  Redirect
} from "react-router-dom"
import { ChannelBrowser, DmBrowser, MessageBoard, Threads } from "../pages"

/**
 * Main Routing for the zc messaging plugin.
 * All other routing must somehow be a descendant of this component.
 */
const Routes = () => (
  <Router>
    <Switch>
      <Route path="/browse-channels" component={ChannelBrowser} />
      <Route path="/threads" component={Threads} />
      <Route path="/all-dms" component={DmBrowser} />
      <Route path="/:roomId" component={MessageBoard} />
      <Route exact path="*">
        <Redirect to="/all-dms" />
      </Route>
    </Switch>
  </Router>
)

export default Routes
