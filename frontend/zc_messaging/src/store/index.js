import { configureStore } from "@reduxjs/toolkit"
import logger from "redux-logger"
import authUserReducer from "./reducers/authUserSlice"
import messageBoardReducer from "./reducers/messageBoardSlice"

export const store = configureStore({
  reducer: {
    authUser: authUserReducer,
    messageBoard: messageBoardReducer
  },
  middleware: getDefaultMiddleware =>
    process.env.NODE_ENV !== "production"
      ? getDefaultMiddleware().concat(logger)
      : getDefaultMiddleware()
})
