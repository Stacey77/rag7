import React from 'react';
import Candidates from './components/Candidates';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG7 - Candidate Management System</h1>
      </header>
      <main>
        <Candidates />
      </main>
    </div>
  );
}

export default App;
