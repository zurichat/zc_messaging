const reducer = (state = {}, action) => {
  switch (action.type) {
    case "value":
      return action.patload
    default:
      return state
  }
}

export default reducer
