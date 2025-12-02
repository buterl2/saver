import { useState } from 'react';

/**
 * Custom hook for password authentication
 */
export const useAuth = (correctPassword) => {
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (password === correctPassword) {
      setIsAuthenticated(true);
    } else {
      alert('Incorrect password!');
    }
  };

  const login = () => {
    if (password === correctPassword) {
      setIsAuthenticated(true);
      return true;
    }
    return false;
  };

  const logout = () => {
    setIsAuthenticated(false);
    setPassword('');
  };

  return {
    password,
    setPassword,
    isAuthenticated,
    handlePasswordSubmit,
    login,
    logout,
  };
};

