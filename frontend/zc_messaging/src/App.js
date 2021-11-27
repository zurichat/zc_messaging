import React from "react"
import { Redirect, Route, Switch } from "react-router-dom"
import AllDms from "./pages/all_dms/AllDms"

// import css styles here
import "bootstrap/dist/css/bootstrap.min.css"

export default function App() {
  return (
    <Switch>
      <Route exact path="/all-dms" component={AllDms} />
      <Route exact path="*">
        <Redirect to="/all-dms" />
      </Route>
    </Switch>
  )
}
