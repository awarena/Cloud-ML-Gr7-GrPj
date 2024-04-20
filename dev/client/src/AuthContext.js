import React, { createContext, useContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // This assumes the JWT is stored under the key 'jwt' in localStorage.
    const jwt = localStorage.getItem('jwt');
    if (jwt) {
      setCurrentUser(jwt);
    }
  }, []);

  const login = (jwt) => {
    localStorage.setItem('jwt', jwt); // Store the JWT in localStorage under the key 'jwt'
    setCurrentUser(jwt); // Update the currentUser state to the new JWT
  };

  const logout = () => {
    localStorage.removeItem('jwt'); // Remove the JWT from localStorage
    setCurrentUser(null); // Reset the currentUser state
  };

  return (
    <AuthContext.Provider value={{ currentUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
