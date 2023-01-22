// Need to use the React-specific entry point to import createApi
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"
import { getCurrentWorkspaceUsers } from "@zuri/utilities"
import { BASE_URL } from "../../utils/constants"

//
const user = JSON.parse(sessionStorage.getItem("user"))
//
// Define a service using a base URL and expected endpoints
export const messagesApi = createApi({
  reducerPath: "messagesApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  // refetchOnFocus: true,
  refetchOnReconnect: true,
  refetchOnMountOrArgChange: true,
  tagTypes: ["Messages"],
  endpoints: builder => ({
    getMessagesInRoom: builder.query({
      async queryFn(_arg, _queryApi, _extraOptions, fetchWithBQ) {
        const { orgId, roomId, pageIndex } = _arg
        const getMessagesInRoomResponse = await fetchWithBQ(
          `/org/${orgId}/rooms/${roomId}/messages?page=${pageIndex}&size=15`
        )

        if (Array.isArray(getMessagesInRoomResponse?.data?.data?.data)) {
          const workspaceUsers = await getCurrentWorkspaceUsers()
          const roomMessages = getMessagesInRoomResponse.data.data.data
          const chatTotal = getMessagesInRoomResponse.data.data.total
          return {
            data: {
              roomMessages: roomMessages
                .reverse()
                .filter(message => message.richUiData && message.timestamp)
                .map(message => {
                  const sender = workspaceUsers.find(
                    user => user._id === message.sender_id
                  )
                  return {
                    ...message,
                    sender: {
                      sender_name: sender?.user_name,
                      sender_image_url: sender?.image_url
                    }
                  }
                }),
              total: chatTotal
            }
          }
        }
        return { data: { roomMessages: [], total: 0 } }
      }
    }),
    sendMessageWithFile: builder.mutation({
      query(data) {
        const { orgId, roomId, messageData } = data
        return {
          url: `/org/${orgId}/rooms/${roomId}/messages`,
          method: "POST",
          headers: {
            token: `${user?.token}`
          },
          body: messageData
        }
      },
      onQueryStarted(
        { orgId, roomId, sender, messageData },
        { dispatch, queryFulfilled }
      ) {
        const patchResult = dispatch(
          messagesApi.util.updateQueryData(
            "getMessagesInRoom",
            { orgId, roomId },
            draft => {
              draft.push({
                sender,
                ...messageData
              })
            }
          )
        )
        queryFulfilled.catch(patchResult.undo)
      }
    }),
    updateMessageInRoom: builder.mutation({
      query(data) {
        const { orgId, roomId, sender, messageData, messageId } = data
        return {
          url: `/org/${orgId}/rooms/${roomId}/messages/${messageId}`,
          method: "PUT",
          body: {
            sender_id: sender.sender_id,
            ...messageData
          }
        }
      },
      invalidatesTags: ["Messages"],
      async onQueryStarted(
        { orgId, roomId, sender, messageData },
        { dispatch, queryFulfilled }
      ) {
        const patchResult = dispatch(
          messagesApi.util.updateQueryData(
            "getMessagesInRoom",
            { orgId, roomId },

            draft => {
              let foundDraft = draft.indexOf(
                draft.find(each => each._id === messageData._id)
              )
              draft[foundDraft] = { sender, ...messageData }
            }
          )
        )
        try {
          await queryFulfilled
          return
        } catch {
          patchResult.undo
        }
      }
    }),
    getMessagesInRoomThreads: builder.query({
      async queryFn(_arg, _queryApi, _extraOptions, fetchWithBQ) {
        const { orgId, roomId, threadId, pageIndex } = _arg
        const getMessagesInRoomResponse = await fetchWithBQ(
          `/org/${orgId}/rooms/${roomId}/messages/${threadId}/threads`
        )
        const parent = await fetchWithBQ(
          `/org/${orgId}/rooms/${roomId}/messages/${threadId}`
        )
        if (Array.isArray(getMessagesInRoomResponse?.data?.data)) {
          const workspaceUsers = await getCurrentWorkspaceUsers()
          const roomMessages = getMessagesInRoomResponse.data.data
          const parentMessage = [parent?.data?.data]
          return {
            data: {
              roomMessages: roomMessages
                .filter(message => message.richUiData && message.timestamp)
                .map(message => {
                  const sender = workspaceUsers.find(
                    user => user._id === message.sender_id
                  )
                  return {
                    ...message,
                    sender: {
                      sender_name: sender?.user_name,
                      sender_image_url: sender?.image_url
                    }
                  }
                }),
              parentMessage: parentMessage
                .filter(message => message.richUiData && message.timestamp)
                .map(message => {
                  const sender = workspaceUsers.find(
                    user => user._id === message.sender_id
                  )
                  return {
                    ...message,
                    sender: {
                      sender_name: sender?.user_name,
                      sender_image_url: sender?.image_url
                    }
                  }
                })
            }
          }
        }
        return { data: { roomMessages: [], parentMessage: [] } }
      }
    }),
    sendMessageInThread: builder.mutation({
      query(data) {
        const { orgId, roomId, threadId, sender, messageData } = data
        return {
          url: `/org/${orgId}/rooms/${roomId}/messages/${threadId}/threads`,
          method: "POST",
          body: {
            sender_id: sender.sender_id,
            ...messageData
          }
        }
      },
      onQueryStarted(
        { orgId, roomId, sender, messageData },
        { dispatch, queryFulfilled }
      ) {
        const patchResult = dispatch(
          messagesApi.util.updateQueryData(
            "getMessagesInRoom",
            { orgId, roomId },
            draft => {
              draft.push({
                sender,
                ...messageData
              })
            }
          )
        )
        queryFulfilled.catch(patchResult.undo)
      }
    })
  })
})

export const {
  useGetMessagesInRoomQuery,
  useSendMessageWithFileMutation,
  useUpdateMessageInRoomMutation,
  useGetMessagesInRoomThreadsQuery,
  useSendMessageInThreadMutation
} = messagesApi
