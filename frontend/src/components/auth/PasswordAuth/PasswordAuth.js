import { useState, useEffect } from 'react';
import './PasswordAuth.css';

function PasswordAuth({ correctPassword, onAuthenticated, title = 'Authentication Required' }) {
  const [password, setPassword] = useState('');

  useEffect(() => {
    // Prevent scrolling when password auth is shown
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    
    return () => {
      // Restore scrolling when component unmounts
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    };
  }, []);

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (password === correctPassword) {
      if (onAuthenticated) {
        onAuthenticated();
      }
    } else {
      alert('Incorrect password!');
    }
  };

  return (
    <div className="password-auth-container">
      <div className="password-auth-form-wrapper">
        <form onSubmit={handlePasswordSubmit}>
          <div className="password-auth-field">
            <label className="password-auth-label">
              Enter Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="password-auth-input"
              autoFocus
            />
          </div>
          <button
            type="submit"
            className="password-auth-button"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default PasswordAuth;

