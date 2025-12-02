import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { fetchPickingData } from '../../services/api';
import { PICKING_PASSWORD, FLOORS, FLOOR_NAMES, FLOW_TYPES } from '../../utils/constants';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import PasswordAuth from '../../components/auth/PasswordAuth/PasswordAuth';
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner';
import FloorTable from '../../components/tables/FloorTable/FloorTable';
import { TbRefresh } from 'react-icons/tb';
import './PickingMonitor.css';

function PickingMonitor() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFlow, setSelectedFlow] = useState(FLOW_TYPES.ALL);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hiddenUsers, setHiddenUsers] = useLocalStorage('picking_hidden_users', []);

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
      const jsonData = await fetchPickingData();
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
          correctPassword={PICKING_PASSWORD}
          title="Picking Monitor"
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
      <h1 className="page-title">Picking Monitor</h1>
      <div className="flow-selector">
        <button 
          className={`flow-button ${selectedFlow === FLOW_TYPES.ALL ? 'active' : ''}`}
          onClick={() => setSelectedFlow(FLOW_TYPES.ALL)}
        >
          All Flows
        </button>
        <button 
          className={`flow-button ${selectedFlow === FLOW_TYPES.A_FLOW ? 'active' : ''}`}
          onClick={() => setSelectedFlow(FLOW_TYPES.A_FLOW)}
        >
          A Flow
        </button>
        <button 
          className={`flow-button ${selectedFlow === FLOW_TYPES.B_FLOW ? 'active' : ''}`}
          onClick={() => setSelectedFlow(FLOW_TYPES.B_FLOW)}
        >
          B Flow
        </button>
        <button className="filter-button" onClick={fetchData} title="Refresh Data" style={{ display: 'flex', alignItems: 'center', gap: '5px', marginLeft: '15px' }}>
          <TbRefresh />
          Refresh
        </button>
        {hiddenUsers.length > 0 && (
          <button className="filter-button" onClick={resetHiddenUsers} style={{ marginLeft: '10px' }}>
            Reset ({hiddenUsers.length} hidden)
          </button>
        )}
      </div>
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.GROUND]} 
        data={data} 
        floor={FLOORS.GROUND} 
        type="picking" 
        selectedFlow={selectedFlow} 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.FIRST]} 
        data={data} 
        floor={FLOORS.FIRST} 
        type="picking" 
        selectedFlow={selectedFlow} 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
      <FloorTable 
        floorName={FLOOR_NAMES[FLOORS.SECOND]} 
        data={data} 
        floor={FLOORS.SECOND} 
        type="picking" 
        selectedFlow={selectedFlow} 
        hiddenUsers={hiddenUsersSet} 
        onToggleUser={toggleUser} 
      />
    </PageLayout>
  );
}

export default PickingMonitor;

