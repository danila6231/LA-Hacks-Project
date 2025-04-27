import React from 'react';
import { CssBaseline, Container } from '@mui/material';
import Microphone from './components/Microphone';

function App() {
  return (
    <>
      <CssBaseline />
      <Container maxWidth="sm">
        <Microphone />
      </Container>
    </>
  );
}

export default App;
