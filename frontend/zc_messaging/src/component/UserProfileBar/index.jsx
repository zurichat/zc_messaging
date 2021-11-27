import React from "react"

const UserProfile = (props) => (
  <>
    <h1>User Profile</h1>
    <p>params: {JSON.stringify(props.match.params)}</p>
  </>
)

export default UserProfile;
