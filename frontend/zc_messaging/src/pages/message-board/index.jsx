import React from "react"
import { Link } from "react-router-dom"
import RightBarRoute from "../../routes/RightBarRoute"
import { Container, MessagingArea, RightAside } from "./MessageBoard.style"

const MessageBoard = props => (
  <Container>
    <MessagingArea>
      {/* todo -> MessageBoard Area */}
      <h1>Messaging</h1>
      <p>params: {JSON.stringify(props.match)}</p>
      <Link to={`${props.match.url}/thread/111`}>Open a thread</Link>
      <br />
      <Link to={`${props.match.url}/member-profile/111`}>
        Open a member full profile
      </Link>
      <br />
      <Link to={`${props.match.url}/channel-details/111`}>
        Open channel details
      </Link>
    </MessagingArea>

    {/* 
      Right sidebar like thread, profile and co
      ... All routed in InMessageRoute component
    */}
    <RightAside>
      <RightBarRoute {...props} />
    </RightAside>
  </Container>
)

export default MessageBoard
