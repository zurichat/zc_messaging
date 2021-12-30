import { createSlice } from "@reduxjs/toolkit"
import messagesData from "../../pages/message-board/messages.data"

const initialState = {
  messages: []
}

export const messageBoardSlice = createSlice({
  name: "messageBoard",
  initialState,
  reducers: {
    addNewMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    setMessages: (state, action) => {
      const filteredMessages = action.payload.filter(
        message => message.richUiData
      )
      state.messages = [...filteredMessages]
    }
  }
})

export const { addNewMessage, setMessages } = messageBoardSlice.actions

export default messageBoardSlice.reducer
