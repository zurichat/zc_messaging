import React from "react"

const DmBrowser = (props) => (
  <>
    <h1>DM Browser</h1>
    <p>params: {JSON.stringify(props.match.params)}</p>
  </>
)

export default DmBrowser;
