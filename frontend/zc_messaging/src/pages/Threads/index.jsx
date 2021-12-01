import React from "react"

const Threads = props => (
  <>
    <h1>Threads</h1>
    <p>params: {JSON.stringify(props.match.params)}</p>
  </>
)

export default Threads
