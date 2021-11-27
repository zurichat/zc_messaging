import React from "react"

const Thread = (props) => (
  <>
    <h1>Thread</h1>
    <p>params: {JSON.stringify(props.match.params)}</p>
  </>
)

export default Thread;
