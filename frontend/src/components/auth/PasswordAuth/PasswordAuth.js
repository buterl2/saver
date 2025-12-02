import { useState } from 'react';
import './PasswordAuth.css';

function PasswordAuth({ correctPassword, onAuthenticated, title = 'Authentication Required' }) {
  const [password, setPassword] = useState('');

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
      <h1 className="page-title">{title}</h1>
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

