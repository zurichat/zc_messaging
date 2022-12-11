import { useState, useEffect } from "react"
import { CommentBoard } from "@zuri/ui"
import { useParams } from "react-router-dom"
import { useSelector } from "react-redux"
import {
  useGetMessagesInRoomThreadsQuery,
  useSendMessageInThreadMutation
} from "../../redux/services/messages.js"

const CommentingBoard = () => {
  const { threadId } = useParams()
  const currentWorkspaceId = localStorage.getItem("currentWorkspace")
  const roomId = window.location.pathname.split("/").at(-3)
  const authUser = useSelector(state => state.authUser)
  const [threadMsg, setThreadMsg] = useState([])
  const [showEmoji, setShowEmoji] = useState(false)
  const [parent, setParent] = useState([])
  const [post, setPost] = useState([])
  const { data: data, isLoading: isLoadingMessages } =
    useGetMessagesInRoomThreadsQuery(
      {
        orgId: currentWorkspaceId,
        roomId,
        threadId
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
    setPost(newMessages)
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
      })
      .catch(() => {
        setPost([])
      })

    return true
  }

  useEffect(() => {
    if (roomId !== "undefined" && threadId) {
      setThreadMsg(data?.roomMessages)
      setParent(data?.parentMessage)
    }
  }, [roomId, threadId, data?.roomMessages])
  return (
    <>
      <CommentBoard
        commentBoardConfig={{ displayCommentBoard: true }}
        messages={threadMsg || []}
        parent={parent || []}
        isLoadingMessages={isLoadingMessages}
        onSendMessage={sendMessageHandler}
        showEmoji={showEmoji}
        setShowEmoji={setShowEmoji}
        isSending={isSending}
        post={post}
      />
    </>
  )
}

export default CommentingBoard
