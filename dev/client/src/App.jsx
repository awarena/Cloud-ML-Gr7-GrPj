import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './Components/Pages/Home';
import Login from './Components/Pages/Login';
import Signup from './Components/Pages/Signup';
import Test from './Components/Pages/Test';
import ProtectedRoute from './Components/ProtectedRoute'; // Ensure this is used correctly

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/test" element={<ProtectedRoute element={<Test />} />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
    </Routes>
  );
}

export default App;
