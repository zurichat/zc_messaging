import React from "react"
import { Route, Switch } from "react-router"
import { ChannelDetails, ThreadBar, UserProfileBar } from "../component"

/**
 * Routes the right bar components: thread, userprofile, channel details
 */
const RightBarRoute = props => {
  const {
    match: { path }
  } = props
  return (
    <Switch>
      <Route exact path={`${path}/thread/:threadId`} component={ThreadBar} />
      <Route
        exact
        path={`${path}/member-profile/:memberId`}
        component={UserProfileBar}
      />
      <Route
        exact
        path={`${path}/channel-details/:channelId`}
        component={ChannelDetails}
      />
    </Switch>
  )
}

export default RightBarRoute
