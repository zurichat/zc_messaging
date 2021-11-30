import App from "./App"
import { BrowserRouter as Router } from "react-router-dom"
import { Provider } from "react-redux"
import { store } from "./store"
import { ChakraProvider } from "@chakra-ui/react"

export default function Root(props) {
  return (
    <Router basename={props.baseName || "/"}>
      <Provider store={store}>
        <ChakraProvider>
          <App />
        </ChakraProvider>
      </Provider>
    </Router>
  )
}
