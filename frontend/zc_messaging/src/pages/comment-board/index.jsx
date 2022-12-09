/* eslint-disable no-console */
import { useState, useEffect } from "react"
import { CommentBoard } from "@zuri/ui"
import { useParams, useOutletContext } from "react-router-dom"
import { useSelector, useDispatch } from "react-redux"
import {
  messagesApi,
  useGetMessagesInRoomThreadsQuery,
  useSendMessageInThreadMutation,
  useUpdateMessageInThreadMutation
} from "../../redux/services/messages.js"

const CommentingBoard = () => {
  const { threadId } = useParams()
  const currentWorkspaceId = localStorage.getItem("currentWorkspace")
  const [pageIndex, setPageIndex] = useState(1)
  const roomId = window.location.pathname.split("/").at(-3)
  const authUser = useSelector(state => state.authUser)
  const [threadMsg, setThreadMsg] = useState([])
  const [showEmoji, setShowEmoji] = useState(false)

  const { data: data, isLoading: isLoadingMessages } =
    useGetMessagesInRoomThreadsQuery(
      {
        orgId: currentWorkspaceId,
        roomId,
        threadId,
        pageIndex
      },
      {
        skip: Boolean(!threadId),
        refetchOnMountOrArgChange: true
      }
    )
  const characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

  function generateString() {
    let result = " "
    const charactersLength = characters.length
    for (let i = 0; i < 10; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength))
    }
    return result
  }
  const [sendNewMessage, { isLoading: isSending }] =
    useSendMessageInThreadMutation()
  const [updateMessage] = useUpdateMessageInThreadMutation()

  const sendMessageHandler = async message => {
    const currentDate = new Date()
    const newMessage = {
      timestamp: currentDate.getTime(),
      emojis: [],
      richUiData: message
    }
    const newMessages = [
      {
        ...newMessage,
        _id: generateString(),
        orgId: currentWorkspaceId,
        roomId,
        sender: {
          sender_id: authUser?.user_id,
          sender_name: authUser?.user_name,
          sender_image_url: authUser?.user_image_url
        }
      }
    ]
    // setIsProcessing({ status: true, message: roomChats.concat(newMessages) })
    sendNewMessage({
      orgId: currentWorkspaceId,
      roomId,
      threadId,
      sender: {
        sender_id: authUser?.user_id,
        sender_name: authUser?.user_name,
        sender_image_url: authUser?.user_image_url
      },
      messageData: { ...newMessage }
    })
      .then(e => {
        const newMessages = [
          {
            ...newMessage,
            _id: e.data.data.message_id,
            orgId: currentWorkspaceId,
            roomId,
            sender: {
              sender_id: authUser?.user_id,
              sender_name: authUser?.user_name,
              sender_image_url: authUser?.user_image_url
            }
          }
        ]
        setThreadMsg(prev => (prev ? prev.concat(newMessages) : newMessages))
        // setIsProcessing({ status: false, message: [] })
      })
      .catch(() => {
        // setIsProcessing({ status: false, message: [] })
      })

    return true
  }

  const reactHandler = (event, emojiObject, messageId) => {
    const currentUserId = authUser?.user_id
    const newMessages = [...threadMsg]

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
          //   Finds the message ID and updates the emojis array for the particular message
          const newState = threadMsg.map(chat => {
            if (chat._id === messageId) {
              return { ...updatedMessage }
            }
            return chat
          })
          //    sets the message array state
          setThreadMsg(newState)
          //
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
      //   Finds the message ID and updates the emojis array for the particular message
      const newState = threadMsg.map(chat => {
        if (chat._id === messageId) {
          return { ...updatedMessage }
        }
        return chat
      })
      //    sets the message array state
      setThreadMsg(newState)
      //
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
    setShowEmoji(false)
    return false
  }

  useEffect(() => {
    if (roomId !== "undefined") {
      setThreadMsg(data?.roomMessages)
    }
  }, [roomId, threadId])
  console.log(threadMsg, data?.roomMessages)
  return (
    <>
      <CommentBoard
        commentBoardConfig={{ displayCommentBoard: true }}
        messages={threadMsg || []}
        isLoadingMessages={isLoadingMessages}
        onSendMessage={sendMessageHandler}
        onReact={reactHandler}
        showEmoji={showEmoji}
        setShowEmoji={setShowEmoji}
      />
    </>
  )
}

export default CommentingBoard
