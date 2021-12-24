import React from "react"
import { GetUserInfo, GetWorkspaceUsers } from "@zuri/utilities"
import AppRoutes from "./routes"
import { useDispatch } from "react-redux"
import { setUser } from "./store/reducers/authUserSlice"

export default function App() {
  const dispatch = useDispatch()
  React.useEffect(() => {
    ;(async () => {
      const userInfo = await GetUserInfo()
      const workspaceUsers = await GetWorkspaceUsers()
      if (userInfo && userInfo.user) {
        dispatch(
          setUser({
            user_id: userInfo.user._id,
            user_name: userInfo.user.user_name,
            user_image_url:
              userInfo.user.image_url ||
              `https://i.pravatar.cc/300?u=${userInfo.user._id}`,
            workspaceUsers
          })
        )
      }
    })()
  }, [])
  return <AppRoutes />
}
