import React, { useState } from "react"
import { useNavigate, useParams, Outlet } from "react-router-dom"
// import { MessageBoard } from "@zuri/zuri-ui"
import { v2 } from "@zuri/zuri-ui"
import mockMessages from "./messages.data.js"
import { Container, MessagingArea, TypingNotice } from "./MessageBoard.style"
import fetchDefaultRoom from "../../utils/fetchDefaultRoom"
import { useSelector } from "react-redux"

const { MessageBoard } = v2
const currentUser = JSON.parse(sessionStorage.getItem("user"))

const MessagingBoard = () => {
  const { roomId } = useParams()
  const navigateTo = useNavigate()
  const [messages, setMessages] = useState(mockMessages)
  const authUser = useSelector(state => state.authUser)
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

  const sendMessageHandler = async message => {
    const currentDate = new Date()
    const currentUser = JSON.parse(sessionStorage.getItem("user"))
    const newMessage = {
      message_id: Date.now().toString(),
      sender: {
        sender_name: currentUser?.username || "Me",
        sender_image_url: currentUser?.imageUrl
      },
      time: `${
        currentDate.getHours() < 12
          ? currentDate.getHours()
          : currentDate.getHours() - 12
      }:${currentDate.getMinutes()}${
        currentDate.getHours() < 12 ? "AM" : "PM"
      }`,
      timestamp: currentDate.getTime(),
      emojis: [],
      richUiData: message
    }
    await Promise.resolve(() => {
      // send message to server
    })
    setMessages([...messages, newMessage])
    return true
  }

  const reactHandler = (event, emojiObject, messageId) => {
    const currentUser = JSON.parse(sessionStorage.getItem("user"))
    const newMessages = [...messages]

    // if message_id is not undefined then it's coming from already rendered emoji in message container

    const emoji = emojiObject.character
    const newEmojiName = messageId ? emojiObject.name : emojiObject.unicodeName

    const messageIndex = newMessages.findIndex(
      message => message.message_id === messageId
    )

    if (messageIndex < 0) {
      return
    }

    const message = newMessages[messageIndex]
    const emojiIndex = message.emojis.findIndex(
      emoji => emoji.name === newEmojiName
    )

    if (emojiIndex >= 0) {
      //the emoji exists in the message
      const reactedUsersId = message.emojis[emojiIndex].reactedUsersId
      const reactedUserIdIndex = reactedUsersId.findIndex(
        id => id === currentUser?.id
      )
      if (reactedUserIdIndex >= 0) {
        // the current user has reacted with this emoji before
        // now, if the user is the only person that has reacted, then the emoji
        // should be removed entirely.
        if (message.emojis[emojiIndex].count <= 1) {
          message.emojis.splice(emojiIndex, 1)
        } else {
          message.emojis[emojiIndex].reactedUsersId.splice(reactedUserIdIndex)
          message.emojis[emojiIndex].count =
            message.emojis[emojiIndex].count - 1
        }
      } else {
        // the user has not reacted and will now be added to the list and count incremented
        message.emojis[emojiIndex].reactedUsersId.push(currentUser?.id)
        message.emojis[emojiIndex].count = message.emojis[emojiIndex].count + 1
      }
    } else {
      // the emoji does not exist
      // create the emoji object and push
      const newEmojiObject = {
        name: newEmojiName,
        count: 1,
        emoji: emoji,
        reactedUsersId: [currentUser?.id]
      }
      message.emojis.push(newEmojiObject)
    }

    newMessages[messageIndex] = message
    setMessages(newMessages)
    return false
  }

  const SendAttachedFileHandler = file => {
    // do something with the file
  }

  return roomId ? (
    <Container>
      <MessagingArea>
        <div style={{ height: "calc(100% - 29px)" }}>
          <MessageBoard
            messages={messages}
            onSendMessage={sendMessageHandler}
            onReact={reactHandler}
            onSendAttachedFile={SendAttachedFileHandler}
            currentUserId={currentUser?.id}
          />
        </div>
        <TypingNotice>Omo Jesu is typing</TypingNotice>
      </MessagingArea>

      {/* 
      Right sidebar like thread, profile and co
      ... All routed in InMessageRoute component
    */}
      <Outlet />
    </Container>
  ) : null
}

export default MessagingBoard
