import { getWorkspaceUsers } from "@zuri/utilities"

/**
 * @param {string} senderId the ID of the sender
 * @returns {Promise<object | null>}
 * @description
 * Find a user(message sender) from users in the workspace.
 * If the user cannot be found, it will return null.
 * If the user is found, it will return the sender information.
 */

const getMessageSender = async senderId => {
  const data = await getWorkspaceUsers()

  return data.users.find(user => user._id === senderId) || null
}

export default getMessageSender
