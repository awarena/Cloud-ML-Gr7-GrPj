import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../AuthContext'; // Adjust path as necessary

const ProtectedRoute = ({ element: Component, ...rest }) => {
  const { currentUser } = useAuth();
  console.log(currentUser)

  return currentUser ? Component : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
