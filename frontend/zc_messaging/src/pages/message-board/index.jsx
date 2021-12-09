import React from "react"
import { useNavigate, useParams, Outlet } from "react-router-dom"
import { MessageBoard } from "@zuri/zuri-ui"
import { Container, MessagingArea, RightAside } from "./MessageBoard.style"
import fetchDefaultRoom from "../../utils/fetchDefaultRoom"

const MessagingBoard = () => {
  const { roomId } = useParams()
  const navigateTo = useNavigate()
  React.useEffect(() => {
    if (!roomId) {
      ;(async () => {
        const currentWorkspaceId = localStorage.getItem("currentWorkspace")
        const currentUser = JSON.parse(sessionStorage.getItem("user"))
        const result = await fetchDefaultRoom(
          currentWorkspaceId,
          currentUser?.id
        )
        navigateTo(`/${result.room_id}`, { replace: true })
      })()
    }
  }, [])
  const chatSidebarConfig = {
    chatHeader: "Chats",
    showChatSideBar: true,
    sendChatMessageHandler: msg => {
      console.warn("sendChatMessageHandler", msg)
      //  dispatch(
      //    handleCreateRoomMessages(authReducer.organisation, room_id, {
      //      sender_id: authReducer.user._id,
      //      room_id,
      //      message: msg.richUiData.blocks[0].text
      //    })
      //  )
    },
    currentUserData: {
      username: "John Doe",
      imageUrl: ""
    },
    messages: []
  }
  return roomId ? (
    <Container>
      <MessagingArea>
        {/* todo -> MessageBoard Area */}
        <MessageBoard messageBoardConfig={chatSidebarConfig} />
        {/* <h1>Messaging</h1>
        <p>params: {JSON.stringify(props.match)}</p>
        <Link to={`${props.match.url}/thread/111`}>Open a thread</Link>
        <br />
        <Link to={`${props.match.url}/member-profile/111`}>
          Open a member full profile
        </Link>
        <br />
        <Link to={`${props.match.url}/channel-details/111`}>
          Open channel details
        </Link> */}
      </MessagingArea>

      {/* 
      Right sidebar like thread, profile and co
      ... All routed in InMessageRoute component
    */}
      <RightAside>
        <Outlet />
      </RightAside>
    </Container>
  ) : null
}

export default MessagingBoard
