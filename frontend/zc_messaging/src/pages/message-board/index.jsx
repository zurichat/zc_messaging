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
        <MessageBoard messageBoardConfig={chatSidebarConfig} />
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
