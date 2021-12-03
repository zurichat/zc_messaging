import React from "react"

const ChannelDetails = props => (
  <>
    <h1>Channel Details</h1>
    <p>params: {JSON.stringify(props.match.params)}</p>
  </>
)

export default ChannelDetails
