import { configureStore } from "@reduxjs/toolkit"
import logger from "redux-logger"
import sampleReducer from "./reducers/templateSlice"

export const store = configureStore({
  reducer: {
    sample: sampleReducer
  },
  middleware: getDefaultMiddleware =>
    process.env.NODE_ENV !== "production"
      ? getDefaultMiddleware().concat(logger)
      : getDefaultMiddleware()
})
