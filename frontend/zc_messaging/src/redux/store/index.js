import { configureStore } from "@reduxjs/toolkit"
import { setupListeners } from "@reduxjs/toolkit/query"
import logger from "redux-logger"
import { messagesApi } from "../services/messages"
import { roomsApi } from "../services/rooms"
import authUserReducer from "./reducers/authUserSlice"

export const store = configureStore({
  reducer: {
    authUser: authUserReducer,
    [messagesApi.reducerPath]: messagesApi.reducer,
    [roomsApi.reducerPath]: roomsApi.reducer
  },
  middleware: getDefaultMiddleware => {
    const middlewares = [messagesApi.middleware, roomsApi.middleware]
    if (process.env.NODE_ENV !== "production") {
      middlewares.push(logger)
    }
    return getDefaultMiddleware().concat(middlewares)
  }
})

setupListeners(store.dispatch)
