import { RightAsideWrapper } from "../../pages/message-board/MessageBoard.style"
import styled from "styled-components"

export const ThreadBar = styled(RightAsideWrapper)`
  /* border: 2px solid red; */
  /* padding-top: 2.8rem; */

  background-color: #fff;
  padding: 0.5px;
  display: flex;
  flex-direction: column;
  gap: 3rem;
`

export const ThreadContent = styled.div`
  border: 2px solid red;
  height: 80vh;
`
export const ThreadBarHeader = styled.div`
  display: flex;
  height: 44px;
  padding: 6px 16px;
  background: #00b87c;
  margin-bottom: -2.6rem;
  z-index: 5;

  align-items: center;
  justify-content: space-between;
  color: red;

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
  /* max-height: calc(100vh - 44px); */
  /* height: 400px; */
  /* margin-right: 1rem; */
  /* height: 100%; */

  /* overflow-y: scroll;
  height: calc(100vh - 250px);

  padding: 0 0.8rem;
  padding-top: 1.78rem;

  &::-webkit-scrollbar {
    display: none;
  } 
  */

  /* flex: 1;
  background: white;
  height: calc(100vh + 50px);
  height: 100%; */
`
