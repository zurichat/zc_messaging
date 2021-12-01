import React from "react"
import { Switch, Route, BrowserRouter as Router } from "react-router-dom"
import Hello from "../component/hello"
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
      <Route exact path="/">
        <div>
          <Hello text="Zuri people" />
          <h2>App is not running on grace!!😊 let's keep it that way</h2>
          <p>
            <strong>Few guide lines</strong>
          </p>
          <ul>
            <li>Make sure to remove console.logs after debugging </li>
            <li>Don't repeat codes, create a reusable component</li>
            <li>Avoid re-rendering!!!</li>
            <li>Don't style elements globally please 😢</li>
            <li>
              Use comments where needed so we can understand what is written
            </li>
          </ul>
        </div>
      </Route>
    </Switch>
  </Router>
)

export default Routes
