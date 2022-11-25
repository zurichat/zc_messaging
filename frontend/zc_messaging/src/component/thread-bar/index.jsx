import React, { useState, useEffect } from "react"
import { FiX } from "react-icons/fi"
import { useNavigate, useParams } from "react-router"
import { Link } from "react-router-dom"
import { MessageBoard, MessageRoomViewHeader, CommentBoard } from "@zuri/ui"
import {
  ThreadContent,
  ThreadBar,
  ThreadBarHeader,
  ThreadBarContent
} from "./ThreadBar.style"
import { useGetRoomsAvailableToUserQuery } from "../../redux/services/rooms"
import { useSelector } from "react-redux"
import {
  messagesApi,
  useGetMessagesInRoomQuery,
  useSendMessageInRoomMutation,
  useUpdateMessageInRoomMutation
} from "../../redux/services/messages.js"

// Function
// =====Time convertion ======
// from 19:09 ro 12hr am/pm
// function tConv24(time24) {
//   let time = new Date(time24).toTimeString()
//   var ts = time.split(" ")[0].slice(0, 5)

//   console.log(
//     time.toLocaleString([], {
//       hour12: false
//     })
//   )
//   var H = +ts.slice(0, 2)
//   var ampm = H < 12 ? " AM" : " PM"
//   ts = H + ts.slice(2, 3) + ampm
//   return ts
// }

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

  // Header component for sidebar thread
  const Header = () => (
    <ThreadBarHeader>
      <span>
        <h4>Thread</h4>

        <h5>
          {roomName}
          {threadId}
        </h5>
      </span>
      <span>
        <Link to={`/${params.roomId || ""}`}>
          <FiX stroke="white" size={18} />
        </Link>
      </span>
    </ThreadBarHeader>
  )

  const commentBoardConfig = {
    displayCommentBoard: true,
    commentBoardHeader: "Hello mike zee",
    sendChatMessageHandler: () => {}
  }

  // Message Api Queries

  const { data: roomMessages, isLoading: isLoadingRoomMessages } =
    useGetMessagesInRoomQuery(
      {
        orgId: currentWorkspaceId,
        roomId
      },
      {
        skip: Boolean(!roomId),
        refetchOnMountOrArgChange: true
      }
    )

  let currentRoomMessage = roomMessages
    ? roomMessages?.filter(messageVal => messageVal._id === threadId)
    : null

  const timeStamp = currentRoomMessage ? currentRoomMessage[0]?.timestamp : ""
  // const newTime = tConv24(timeStamp)
  // console.log("Current id", currentRoomMessage)

  return (
    <>
      {/*
      <ThreadBarHeader>
        <span>
          <h4>Thread</h4>

          <h5>{roomName}</h5>

          <h6>{params.threadId} </h6>
        </span>
        <span>
          <Link to={`/${params.roomId || ""}`}>
            <FiX stroke="white" size={18} />
          </Link>
        </span>
      </ThreadBarHeader>
   

      */}

      <ThreadBar>
        <Header />
        <ThreadContent>
          <section>
            <div>
              <img
                src={
                  currentRoomMessage &&
                  (currentRoomMessage[0]?.sender?.sender_image_url == ""
                    ? `https://i.pravatar.cc/300?u=637d3508601ce3fc5dc7364f`
                    : currentRoomMessage[0]?.sender?.sender_image_url)
                }
                alt="user picture"
              />
            </div>
            <div>
              {currentRoomMessage && (
                <p>
                  {currentRoomMessage[0]?.sender?.sender_name}
                  <span>time</span>
                </p>
              )}

              {currentRoomMessage && (
                <p className="room__message">
                  {" "}
                  {currentRoomMessage[0]?.richUiData.blocks[0].text}
                </p>
              )}
            </div>
          </section>
        </ThreadContent>
        <div>{threadId}</div>
        {/* <TypingNotice>Omo Jesu is typing</TypingNotice> */}
      </ThreadBar>
      {/* <TypingNotice>Omo Jesu is typing</TypingNotice> */}
    </>
  )
}

export default Thread
