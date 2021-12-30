import { createSlice } from "@reduxjs/toolkit"

const initialState = {
  user_id: "",
  user_name: "",
  user_image_url: "",
  workspaceUsers: {}
}

export const authUserSlice = createSlice({
  name: "authUser",
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user_id = action.payload.user_id
      state.user_name = action.payload.user_name
      state.user_image_url = action.payload.user_image_url
      state.workspaceUsers = action.payload.workspaceUsers
    }
  }
})

export const { setUser } = authUserSlice.actions

export default authUserSlice.reducer
