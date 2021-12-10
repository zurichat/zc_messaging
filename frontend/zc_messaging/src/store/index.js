import { configureStore } from "@reduxjs/toolkit"
import logger from "redux-logger"
import authUserReducer from "./reducers/authUserSlice"

export const store = configureStore({
  reducer: {
    authUser: authUserReducer
  },
  middleware: getDefaultMiddleware =>
    process.env.NODE_ENV !== "production"
      ? getDefaultMiddleware().concat(logger)
      : getDefaultMiddleware()
})
