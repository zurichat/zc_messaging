// Need to use the React-specific entry point to import createApi
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"
import { GetWorkspaceUsers } from "@zuri/utilities"
import { BASE_URL } from "../../utils/constants"

// Define a service using a base URL and expected endpoints
export const messagesApi = createApi({
  reducerPath: "messagesApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  endpoints: builder => ({
    getMessagesInRoom: builder.query({
      async queryFn(_arg, _queryApi, _extraOptions, fetchWithBQ) {
        const { orgId, roomId } = _arg
        const getMessagesInRoomResponse = await fetchWithBQ(
          `/org/${orgId}/rooms/${roomId}/messages`
        )
        if (Array.isArray(getMessagesInRoomResponse.data.data)) {
          const workspaceUsers = await GetWorkspaceUsers()
          const roomMessages = getMessagesInRoomResponse.data.data
          return {
            data: roomMessages
              .filter(message => message.richUiData && message.timestamp)
              .map(message => {
                const sender = workspaceUsers.users.find(
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
        return []
      }
    }),
    sendMessageInRoom: builder.mutation({
      query(data) {
        const { orgId, roomId, sender, messageData } = data
        return {
          url: `/org/${orgId}/rooms/${roomId}/messages`,
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

export const { useGetMessagesInRoomQuery, useSendMessageInRoomMutation } =
  messagesApi
