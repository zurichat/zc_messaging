import axios from "axios"

/**
 * @param {string} orgId
 * @param {string} userId
 * @returns {Promise<{room_id: string}> | {room_id: undefined}}
 * @description
 * Fetches the default room for the user.
 * If the user has no default room, it will return the first public room.
 * If the user has no public rooms, it will return an empty object.
 * @see https://chat.zuri.chat/api/v1/sidebar?org=orgId&user=userId
 */

const fetchDefaultRoom = async (orgId, userId) => {
  const response = await axios.get(
    `https://chat.zuri.chat/api/v1/sidebar?org=${orgId}&user=${userId}`
  )
  const { public_rooms } =
    response.data?.data?.find(room => room.name === "Channels") || {}
  const defaultRoom =
    public_rooms?.find(room => room.room_name === "general") || {}
  return {
    room_id: defaultRoom.room_id
  }
}

export default fetchDefaultRoom
