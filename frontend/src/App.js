import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Candidates from './components/Candidates';

// Simple route guard
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/candidates"
          element={
            <PrivateRoute>
              <Candidates />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/candidates" />} />
      </Routes>
    </Router>
  );
}

export default App;
