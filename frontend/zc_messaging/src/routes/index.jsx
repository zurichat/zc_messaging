import React from "react"
import { Routes, Route } from "react-router-dom"
import { ThreadBar, UserProfileBar, ChannelDetails } from "../component"
import { ChannelBrowser, DmBrowser, MessagingBoard, Threads } from "../pages"

/**
 * Main Routing for the zc messaging plugin.
 * All other routing must somehow be a descendant of this component.
 */
const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<MessagingBoard />} />
    <Route path="/:roomId" element={<MessagingBoard />}>
      <Route path="thread/:threadId" element={<ThreadBar />} />
      <Route path="member-profile/:memberId" element={<UserProfileBar />} />
      <Route path="channel-details/:channelId" element={<ChannelDetails />} />
    </Route>
    <Route path="/browse-channels" element={<ChannelBrowser />} />
    <Route path="/threads" element={<Threads />} />
    <Route path="/all-dms" element={<DmBrowser />} />
  </Routes>
)

export default AppRoutes
