import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { fetchPackingData } from '../../services/api';
import { PACKING_PASSWORD, FLOORS, FLOOR_NAMES } from '../../utils/constants';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import PasswordAuth from '../../components/auth/PasswordAuth/PasswordAuth';
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner';
import FloorTable from '../../components/tables/FloorTable/FloorTable';
import { TbRefresh } from 'react-icons/tb';
import './PackingMonitor.css';

function PackingMonitor() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hiddenUsers, setHiddenUsers] = useLocalStorage('packing_hidden_users', []);

  // Convert array to Set for filtering
  const hiddenUsersSet = new Set(hiddenUsers);

  const toggleUser = (username) => {
    const newHidden = new Set(hiddenUsersSet);
    if (newHidden.has(username)) {
      newHidden.delete(username);
    } else {
      newHidden.add(username);
    }
    setHiddenUsers(Array.from(newHidden));
  };

  const resetHiddenUsers = () => {
    setHiddenUsers([]);
  };

  const fetchData = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const jsonData = await fetchPackingData();
      setData(jsonData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated, fetchData]);

  if (!isAuthenticated) {
    return (
      <PageLayout>
        <PasswordAuth 
          correctPassword={PACKING_PASSWORD}
          title="Packing Monitor"
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
      <h1 className="page-title">Packing Monitor</h1>
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px', gap: '10px' }}>
        <button className="filter-button" onClick={fetchData} title="Refresh Data" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <TbRefresh />
          Refresh
        </button>
        {hiddenUsers.length > 0 && (
          <button className="filter-button" onClick={resetHiddenUsers}>
            Reset ({hiddenUsers.length} hidden)
          </button>
        )}
      </div>
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.GROUND]} 
        data={data} 
        floor={FLOORS.GROUND} 
        type="packing" 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.FIRST]} 
        data={data} 
        floor={FLOORS.FIRST} 
        type="packing" 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.SECOND]} 
        data={data} 
        floor={FLOORS.SECOND} 
        type="packing" 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
    </PageLayout>
  );
}

export default PackingMonitor;

