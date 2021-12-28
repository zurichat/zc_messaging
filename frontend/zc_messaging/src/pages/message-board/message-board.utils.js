import axios from "axios"
import { BASE_URL } from "../../utils/constants"

/**
 * @param {string} orgId
 * @param {string} roomId
 * @param {string} senderId
 * @param {Object} messageData
 * @returns {Promise<Object>}
 * @description Send message to the room and persist message in the database
 */

const sendMessageBoardHandler = async (
  orgId,
  roomId,
  senderId,
  messageData
) => {
  try {
    if (orgId && roomId && senderId && messageData) {
      const sendMessageResponse = await axios.post(
        // `https://chat.zuri.chat/api/v1/org/${orgId}/rooms/${roomId}/messages`,
        `${BASE_URL}/org/${orgId}/rooms/${roomId}/messages`,
        {
          sender_id: senderId,
          ...messageData
        }
      )
      return sendMessageResponse.data
    }
    throw new Error("Invalid arguments")
  } catch (error) {
    console.error(error)
  }
}

/**
 * @param {string} orgId organization ID
 * @param {string} roomId room ID
 * @returns {Promise<Object>}
 * @description Retrieve all room messages
 */

const getRoomMessagesHandler = async (orgId, roomId) => {
  try {
    if (orgId && roomId) {
      const getRoomMessagesResponse = await axios.get(
        `${BASE_URL}/org/${orgId}/rooms/${roomId}/messages`
      )
      return getRoomMessagesResponse.data
    }
    throw new Error("Invalid arguments")
  } catch (error) {
    console.error(error)
  }
}

export { sendMessageBoardHandler, getRoomMessagesHandler }
