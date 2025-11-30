import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Candidates from './components/Candidates';

function App() {
  const isAuthenticated = () => {
    return !!localStorage.getItem('access_token');
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/candidates"
          element={isAuthenticated() ? <Candidates /> : <Navigate to="/login" />}
        />
        <Route path="/" element={<Navigate to="/candidates" />} />
      </Routes>
    </Router>
  );
}

export default App;
