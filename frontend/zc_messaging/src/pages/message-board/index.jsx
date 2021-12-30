import React, { useState } from "react"
import { useNavigate, useParams, Outlet } from "react-router-dom"
import { MessageBoard } from "@zuri/zuri-ui"
import { SubscribeToChannel } from "@zuri/utilities"
import mockMessages from "./messages.data.js"
import { Container, MessagingArea, TypingNotice } from "./MessageBoard.style"
import fetchDefaultRoom from "../../utils/fetchDefaultRoom"
import { useSelector, useDispatch } from "react-redux"
import {
  getRoomMessagesHandler,
  sendMessageBoardHandler
} from "./message-board.utils"
import {
  addNewMessage,
  setMessages
} from "../../store/reducers/messageBoardSlice"

const MessagingBoard = () => {
  const { roomId } = useParams()
  const navigateTo = useNavigate()
  const dispatch = useDispatch()
  const userMessages = useSelector(state => state.messageBoard.messages)
  const authUser = useSelector(state => state.authUser)
  const currentWorkspaceId = localStorage.getItem("currentWorkspace")
  React.useEffect(() => {
    if (!roomId) {
      ;(async () => {
        const result = await fetchDefaultRoom(
          currentWorkspaceId,
          authUser?.user_id
        )
        navigateTo(`/${result.room_id}`, { replace: true })
      })()
    }
  }, [])

  React.useEffect(() => {
    if (roomId && authUser.user_id) {
      getRoomMessagesHandler(currentWorkspaceId, roomId).then(data => {
        dispatch(setMessages(data.data))
      })
      SubscribeToChannel(roomId, data => {
        if (data.data.data.sender_id !== authUser.user_id) {
          const sender = authUser?.workspaceUsers.users.find(
            user => user._id === data.data.data.sender_id
          )
          dispatch(
            addNewMessage({
              ...data.data.data,
              sender: {
                sender_name: sender?.user_name,
                sender_image_url: sender?.image_url
              }
            })
          )
        }
      })
    }
  }, [roomId, authUser])

  const sendMessageHandler = async message => {
    const currentDate = new Date()
    const newMessage = {
      sender_id: authUser?.user_id,
      timestamp: currentDate.getTime(),
      emojis: [],
      richUiData: message
    }
    const sender = authUser?.workspaceUsers.users.find(
      user => user._id === authUser?.user_id
    )
    dispatch(
      addNewMessage({
        ...newMessage,
        sender: {
          sender_name: sender?.user_name,
          sender_image_url: sender?.image_url
        }
      })
    )
    const response = await sendMessageBoardHandler(
      currentWorkspaceId,
      roomId,
      authUser?.user_id,
      newMessage
    )
    return true
  }

  const reactHandler = (event, emojiObject, messageId) => {
    const currentUserId = authUser?.user_id
    const newMessages = [...userMessages]

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
        id => id === currentUserId
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
        // console.log("reacted-user-id-index", message.emojis[emojiIndex])
        // console.log("id", currentUserId)
        // console.log("type", isArray(message.emojis[emojiIndex].reactedUsersId))
        message.emojis[emojiIndex].reactedUsersId = [
          ...message.emojis[emojiIndex].reactedUsersId,
          currentUserId
        ]
        // message.emojis[emojiIndex].count = message.emojis[emojiIndex].count + 1
      }
    } else {
      // the emoji does not exist
      // create the emoji object and push
      const newEmojiObject = {
        name: newEmojiName,
        count: 1,
        emoji: emoji,
        reactedUsersId: [currentUserId]
      }
      message.emojis.push(newEmojiObject)
    }

    newMessages[messageIndex] = message
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
            messages={(() => {
              return userMessages.map(message => {
                const sender = authUser?.workspaceUsers.users.find(
                  user => user._id === message.sender_id
                )
                return {
                  ...message,
                  timestamp: new Date().getTime(),
                  sender: {
                    sender_name: sender?.user_name,
                    sender_image_url: sender?.image_url
                  }
                }
              })
            })()}
            onSendMessage={sendMessageHandler}
            onReact={reactHandler}
            onSendAttachedFile={SendAttachedFileHandler}
            currentUserId={authUser?.user_id}
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
