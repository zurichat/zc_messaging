import axios from "axios"
import { BASE_URL } from "../../utils/constants"

/**
 * @param {string} orgId
 * @param {string} senderId
 * @returns {Promise<Object>}
 * @description Send get thread of all message from Database senderId is associated with
 */

const getThreadHandler = async (orgId, senderId) => {
  try {
    if (orgId && senderId) {
      const getThreadRequest = await axios.get(
        // `${BASE_URL}/org/${orgId}/member/${senderId}/threads`
        `${BASE_URL}/org/${orgId}/member/${senderId}/threads`
      )
      return getThreadRequest.data
      // catch error is handled in ./index.jsx where getThreadRequest is called
      // Like so getThreadRequest.then().catch(err) // do something
    }
  } catch (error) {
    console.error(error)
  }
}

export { getThreadHandler }
