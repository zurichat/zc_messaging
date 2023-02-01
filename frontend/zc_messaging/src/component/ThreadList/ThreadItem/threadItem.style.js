import styled from "styled-components"

export const ThreadItemWrapper = styled.section`
  border: 1px solid black;
  padding: 20px 20px;
  display: flex;
  flex-direction: column;
  margin: 10px auto;
  width: 92%;
  border-radius: 12px;

  & > .sender_cont_34f4 {
    display: flex;
    justify-content: space-between;
    padding: 0 24px 0 0;
  }

  & > .date_sent_34f4 {
    color: #252323;
    font-size: 13px;
    font-weight: 500;
  }

  & > .thread_text_cont_45gm6 {
    p {
      font-size: 23px;
      font-weight: 600;
      color: #000;
    }
  }
`
