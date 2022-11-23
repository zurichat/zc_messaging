import React, { useState, useEffect } from "react"
import { FiX } from "react-icons/fi"
import { useNavigate, useParams } from "react-router"
import { Link } from "react-router-dom"
import { MessageBoard } from "@zuri/ui"
import { ThreadBar, ThreadBarHeader, ThreadBarContent } from "./ThreadBar.style"
import { useGetRoomsAvailableToUserQuery } from "../../redux/services/rooms"
import { useSelector } from "react-redux"
import {
  messagesApi,
  useGetMessagesInRoomQuery,
  useSendMessageInRoomMutation,
  useUpdateMessageInRoomMutation
} from "../../redux/services/messages.js"

const Thread = () => {
  const navigate = useNavigate()
  const authUser = useSelector(state => state.authUser)
  const params = useParams()
  const { threadId } = useParams()
  const { roomId } = useParams()
  const [roomName, setRoomName] = useState("unknown-channel")
  const currentWorkspaceId = localStorage.getItem("currentWorkspace")

  const { data: roomsAvailable, isLoading: IsLoadingRoomsAvailable } =
    useGetRoomsAvailableToUserQuery(
      {
        orgId: currentWorkspaceId,
        userId: authUser.user_id
      },
      {
        skip: Boolean(!authUser.user_id),
        refetchOnMountOrArgChange: true
      }
    )

  useEffect(() => {
    if (roomsAvailable) {
      const room = roomsAvailable[roomId]
      setRoomName(room?.room_name)
    }
  }, [roomId, roomsAvailable])

  // Message sending

  const [sendNewMessage, { isLoading: isSending }] =
    useSendMessageInRoomMutation()

  const sendMessageHandler = async message => {
    const currentDate = new Date()
    const newMessage = {
      timestamp: currentDate.getTime(),
      emojis: [],
      richUiData: message
    }
    sendNewMessage({
      orgId: currentWorkspaceId,
      roomId,
      sender: {
        sender_id: authUser?.user_id,
        sender_name: authUser?.user_name,
        sender_image_url: authUser?.user_image_url
      },
      messageData: { ...newMessage }
    })
    return true
  }

  return (
    <ThreadBar>
      <ThreadBarHeader>
        <span>
          <h4>Thread</h4>

          <h5>{roomName}</h5>
        </span>
        <span>
          <Link to={`/${params.roomId || ""}`}>
            <FiX stroke="white" size={18} />
          </Link>
        </span>
      </ThreadBarHeader>
      <div className="content-wrapper">
        <ThreadBarContent>
          {/* <MessageCard /> */} Thread id {params.threadId}{" "}
        </ThreadBarContent>

        <div>
          <MessageBoard onSendMessage={sendMessageHandler} />
        </div>
      </div>
    </ThreadBar>
  )
}

export default Thread
