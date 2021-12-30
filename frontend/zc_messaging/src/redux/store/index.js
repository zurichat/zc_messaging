import { configureStore } from "@reduxjs/toolkit"
import logger from "redux-logger"
import { messagesApi } from "../services/messages"
import authUserReducer from "./reducers/authUserSlice"

export const store = configureStore({
  reducer: {
    authUser: authUserReducer,
    [messagesApi.reducerPath]: messagesApi.reducer
  },
  middleware: getDefaultMiddleware => {
    const middlewares = [messagesApi.middleware]
    if (process.env.NODE_ENV !== "production") {
      middlewares.push(logger)
    }
    return getDefaultMiddleware().concat(middlewares)
  }
})
