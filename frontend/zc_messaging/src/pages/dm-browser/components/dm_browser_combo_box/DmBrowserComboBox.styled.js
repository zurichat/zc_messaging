import styled from "styled-components"

const AllDmsComboBoxContainer = styled.div`
  min-height: 56px;
  padding: 0.625rem 1rem;
  background: #fff;
  display: flex;
  align-items: center;

  > P {
    margin: 0 0.625rem 0 0;
    font-size: 0.812rem;
  }
`

const AllDmsComboBoxContent = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  width: 100%;

  > input {
    width: 100%;
    outline: none;
    border: none;
  }
`

export { AllDmsComboBoxContainer, AllDmsComboBoxContent }
