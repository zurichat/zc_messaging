import { useEffect, useState } from "react"
import { useNavigate, useParams, Outlet } from "react-router-dom"
import { Helmet } from "react-helmet"
import { MessageBoard, MessageRoomViewHeader } from "@zuri/ui"
import { subscribeToChannel } from "@zuri/utilities"
import { Container, MessagingArea, TypingNotice } from "./MessageBoard.style"
import fetchDefaultRoom from "../../utils/fetchDefaultRoom"
import { useSelector, useDispatch } from "react-redux"
import getMessageSender from "../../utils/getMessageSender.js"
import {
  messagesApi,
  useGetMessagesInRoomQuery,
  useSendMessageInRoomMutation,
  useUpdateMessageInRoomMutation
} from "../../redux/services/messages.js"
import { useGetRoomsAvailableToUserQuery } from "../../redux/services/rooms"
import generatePageTitle from "../../utils/generatePageTitle"

const MessagingBoard = () => {
  const { roomId } = useParams()
  const navigateTo = useNavigate()
  const dispatch = useDispatch()
  const authUser = useSelector(state => state.authUser)
  const currentWorkspaceId = localStorage.getItem("currentWorkspace")
  const [pageTitle, setPageTitle] = useState("")
  const [roomName, setRoomName] = useState("unknown-channel")
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
  const [sendNewMessage, { isLoading: isSending }] =
    useSendMessageInRoomMutation()

  const [updateMessage] = useUpdateMessageInRoomMutation()

  useEffect(() => {
    if (!roomId) {
      fetchDefaultRoom(currentWorkspaceId, authUser?.user_id).then(result => {
        navigateTo(`/${result.room_id}`, { replace: true })
      })
    }
    if (roomId && authUser.user_id) {
      subscribeToChannel(roomId, data => {
        if (data.data.data.sender_id !== authUser.user_id) {
          getMessageSender(data.data.data.sender_id).then(sender => {
            dispatch(
              messagesApi.util.updateQueryData(
                "getMessagesInRoom",
                {
                  orgId: currentWorkspaceId,
                  roomId
                },
                draftMessages => {
                  draftMessages.push({
                    sender: {
                      sender_name: sender?.user_name,
                      sender_image_url:
                        sender?.image_url ||
                        `https://i.pravatar.cc/300?u=${sender?._id}`
                    },
                    ...data.data.data
                  })
                }
              )
            )
          })
        }
      })
    }
  }, [roomId, authUser])

  useEffect(() => {
    if (roomsAvailable) {
      const room = roomsAvailable[roomId]
      setRoomName(room?.room_name)
      setPageTitle(generatePageTitle(room?.room_name))
    }
  }, [roomId, roomsAvailable])

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

  const reactHandler = (event, emojiObject, messageId) => {
    const currentUserId = authUser?.user_id
    const newMessages = [...roomMessages]

    // if message_id is not undefined then it's coming from already rendered emoji in message container

    const emoji = emojiObject.character
    const newEmojiName = emojiObject.unicodeName || emojiObject.name
    const messageIndex = newMessages.findIndex(
      message => message._id === messageId
    )

    if (messageIndex < 0) {
      return
    }

    const message = newMessages[messageIndex]
    const emojiIndex = message.emojis.findIndex(
      emoji => emoji.name.toLowerCase() === newEmojiName.toLowerCase()
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
          let emojisArray = message.emojis.filter(
            emoji => emoji.name.toLowerCase() !== newEmojiName.toLowerCase()
          )
          let updatedMessage = {
            ...message,
            emojis: emojisArray,
            edited: true,
            message_id: messageId
          }
          updateMessage({
            orgId: currentWorkspaceId,
            roomId,
            sender: {
              sender_id: authUser?.user_id,
              sender_name: authUser?.user_name,
              sender_image_url: authUser?.user_image_url
            },
            messageData: { ...updatedMessage },
            messageId: updatedMessage._id
          })
          // message.emojis.splice(emojiIndex, 1)
        } else {
          message.emojis[emojiIndex].reactedUsersId.splice(reactedUserIdIndex)
          message.emojis[emojiIndex].count =
            message.emojis[emojiIndex].count - 1
        }
      } else {
        // the user has not reacted and will now be added to the list and count incremented

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
      let emojisArray = [...message.emojis, newEmojiObject]
      let updatedMessage = {
        ...message,
        emojis: emojisArray,
        edited: true,
        message_id: messageId
      }

      updateMessage({
        orgId: currentWorkspaceId,
        roomId,
        sender: {
          sender_id: authUser?.user_id,
          sender_name: authUser?.user_name,
          sender_image_url: authUser?.user_image_url
        },
        messageData: { ...updatedMessage },
        messageId: updatedMessage._id
      })
    }

    return false
  }

  const SendAttachedFileHandler = file => {
    // do something with the file
  }

  return roomId ? (
    <>
      <Helmet>
        <title>{pageTitle}</title>
      </Helmet>
      <MessageRoomViewHeader name={`#${roomName}`} />
      <Container>
        <MessagingArea>
          <div style={{ height: "100%" }}>
            <MessageBoard
              isLoadingMessages={isLoadingRoomMessages}
              messages={roomMessages || []}
              onSendMessage={sendMessageHandler}
              onReact={reactHandler}
              onSendAttachedFile={SendAttachedFileHandler}
              currentUserId={authUser?.user_id}
              height={"92vh"}
            />
          </div>
          {/* <TypingNotice>Omo Jesu is typing</TypingNotice> */}
        </MessagingArea>

        {/* 
      Right sidebar like thread, profile and co
      ... All routed in InMessageRoute component
    */}
        <Outlet />
      </Container>
    </>
  ) : null
}

export default MessagingBoard
