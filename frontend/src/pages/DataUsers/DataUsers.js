import { useState, useEffect } from 'react';
import { fetchUsersNames, saveUsersNames } from '../../services/api';
import { DATA_USERS_PASSWORD } from '../../utils/constants';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import PasswordAuth from '../../components/auth/PasswordAuth/PasswordAuth';
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner';
import './DataUsers.css';

function DataUsers() {
  const [allUsers, setAllUsers] = useState([]);
  const [userNames, setUserNames] = useState({});
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      const loadData = async () => {
        try {
          const users = await fetchUsersNames();
          setAllUsers(users);
          const names = await fetchUsersNames();
          setUserNames(names);
        } catch (error) {
          console.error('Error fetching data:', error);
        } finally {
          setLoading(false);
        }
      };
      loadData();
    }
  }, [isAuthenticated]);

  const handleNameChange = (username, newName) => {
    setUserNames({
      ...userNames,
      [username]: newName
    });
  };

  const handleSave = async () => {
    try {
      await saveUsersNames(userNames);
      alert('Names saved successfully!');
    } catch (error) {
      console.error('Error saving names:', error);
      alert('Failed to save names!');
    }
  };

  if (!isAuthenticated) {
    return (
      <PageLayout>
        <PasswordAuth 
          correctPassword={DATA_USERS_PASSWORD}
          title="Data Users Management"
          onAuthenticated={() => setIsAuthenticated(true)}
        />
      </PageLayout>
    );
  }

  if (loading) {
    return (
      <PageLayout>
        <LoadingSpinner message="Loading..." />
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <h1 className="page-title">Data Users Management</h1>
      
      <div className="data-users-container">
        <div className="data-users-list">
          {allUsers.sort().map(username => (
            <div key={username} className="data-users-item">
              <label className="data-users-label">
                {username}
              </label>
              <input
                type="text"
                value={userNames[username] || ''}
                onChange={(e) => handleNameChange(username, e.target.value)}
                placeholder="Enter name..."
                className="data-users-input"
              />
            </div>
          ))}
        </div>
        
        <button
          onClick={handleSave}
          className="data-users-save-button"
          onMouseOver={(e) => {
            e.target.style.background = '#ebe9ff';
            e.target.style.color = 'black';
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'transparent';
            e.target.style.color = 'white';
          }}
        >
          Save Names
        </button>
      </div>
    </PageLayout>
  );
}

export default DataUsers;

