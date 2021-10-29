import App from "./App"
import { Provider } from "react-redux"
import { store } from "./store"
import { ChakraProvider } from "@chakra-ui/react"

export default function Root() {
  return (
    <Provider store={store}>
      <ChakraProvider>
        <App />
      </ChakraProvider>
    </Provider>
  )
}
