import { RightAsideWrapper } from "../../pages/message-board/MessageBoard.style"
import styled from "styled-components"

export const ThreadBar = styled(RightAsideWrapper)``

export const ThreadBarHeader = styled.div`
  display: flex;
  height: 44px;
  padding: 6px 16px;
  background: #00b87c;
  align-items: center;
  justify-content: space-between;

  & > span {
    display: flex;
    align-items: center;

    & > :is(h4, h5) {
      margin: 0;
    }

    & > h4 {
      font-size: 18px;
      color: white;
    }

    & > h5 {
      font-size: 13px;
      color: #c5ebde;
      font-weight: normal;
      margin-left: 8px;

      &::before {
        content: "#";
      }
    }

    a {
      text-decoration: none;
      cursor: pointer;
    }
  }
`

export const ThreadBarContent = styled.div`
  max-height: calc(100vh - 44px);
  height: 400px;
  margin-right: 1rem;
  background: white;
`
