import App from "./App"
import { BrowserRouter as Router } from "react-router-dom"
import { Provider } from "react-redux"
import { store } from "./redux/store"
import "./root-component.css"

export default function Root(props) {
  return (
    <Router basename={props.baseName || "/"}>
      <Provider store={store}>
        <App />
      </Provider>
    </Router>
  )
}
