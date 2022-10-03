// Need to use the React-specific entry point to import createApi
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"
import { BASE_URL } from "../../utils/constants"

// Define a service using a base URL and expected endpoints
export const roomsApi = createApi({
  reducerPath: "roomsApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  endpoints: builder => ({
    getRoomsAvailableToUser: builder.query({
      async queryFn(_arg, _queryApi, _extraOptions, fetchWithBQ) {
        const { orgId, userId } = _arg
        const getUserSidebarData = await fetchWithBQ(
          `/sidebar?org=${orgId}&user=${userId}`
        )
        const roomsAvailable = {}
        if (Array.isArray(getUserSidebarData?.data?.data)) {
          let roomsAvailableToUser = []
          getUserSidebarData.data.data.forEach(category => {
            if (
              category.name === "Channels" ||
              category.name === "Direct Messages"
            ) {
              roomsAvailableToUser = [
                ...roomsAvailableToUser,
                ...category.public_rooms,
                ...category.joined_rooms
              ]
            }
          })
          roomsAvailableToUser.forEach(room => {
            roomsAvailable[room.room_id] = room
          })
        }
        return { data: roomsAvailable }
      }
    })
  })
})

export const { useGetRoomsAvailableToUserQuery } = roomsApi
