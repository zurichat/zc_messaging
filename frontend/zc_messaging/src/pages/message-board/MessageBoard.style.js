import styled from "styled-components"

export const Container = styled.main`
  display: flex;
  height: 100%;
  /* padding-top: 1.93rem; */
  gap: 8px;
  background: #f9f9f9;
`

// Main Area chatting
export const MessagingArea = styled.div`
  flex: 1;
  background: white;
  height: calc(100vh + 50px);
  height: 100%;
`

// Sidebar for trend
export const RightAsideWrapper = styled.div`
  width: 415px;
  z-index: 3;
`
export const TypingNotice = styled.div`
  height: 29px;
  display: flex;
  align-items: center;
  padding-inline: 18px;

  font-family: Lato;
  font-style: italic;
  font-weight: normal;
  font-size: 12px;
  line-height: 130%;
  color: #b0afb0;
`
