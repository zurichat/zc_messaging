import axios from "axios"

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
