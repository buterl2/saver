import { HOURS } from '../../../utils/constants';
import './FloorTable.css';

function FloorTable({ floorName, data, floor, type = "picking", selectedFlow = "all", hiddenUsers = new Set(), onToggleUser = null }) {
  const getFloorData = () => {
    if (!data) return [];
    
    const floorUsers = [];
    
    for (const [username, userFloors] of Object.entries(data)) {
      if (userFloors[floor]) {
        const floorData = userFloors[floor];
        
        const userRow = {
          username: username,
          name: userFloors.name || 'Unknown',
          ratio: 0,
          items_picked: 0,
          hourCounts: {},
          hourColors: {},
          total: 0,
          hoursWorked: 0,
          productivity: 0,
          productivityColor: null
        };
        
        if (type === "packing") {
          // PACKING logic stays the same
          userRow.hoursWorked = floorData.hours_worked || 0;
          userRow.productivity = floorData.productivity || 0;
          userRow.productivityColor = floorData.productivity_color;
          
          HOURS.forEach(hour => {
            if (floorData[hour]) {
              userRow.hourCounts[hour] = floorData[hour].count;
              userRow.hourColors[hour] = floorData[hour].productivity_color;
              userRow.total += floorData[hour].count;
            }
          });
          
        } else {
          // PICKING: Filter by selected flow
          for (const [flowName, flowData] of Object.entries(floorData)) {
            if (typeof flowData !== 'object') continue;
            
            // FILTER: Skip flows that don't match the selection
            if (selectedFlow !== 'all' && flowName !== selectedFlow) {
              continue; // Skip this flow
            }
            
            // Add hours worked and productivity
            if (flowData.hours_worked) {
              userRow.hoursWorked = flowData.hours_worked;
              userRow.productivity = flowData.productivity;
              userRow.ratio = flowData.ratio;
              userRow.items_picked = flowData.items_picked;
              userRow.productivityColor = flowData.productivity_color;
            }
            
            // Add hour counts and colors
            HOURS.forEach(hour => {
              if (flowData[hour]) {
                if (!userRow.hourCounts[hour]) {
                  userRow.hourCounts[hour] = 0;
                }
                userRow.hourCounts[hour] += flowData[hour].count;
                userRow.hourColors[hour] = flowData[hour].productivity_color;
                userRow.total += flowData[hour].count;
              }
            });
          }
        }
        
        // Only add user if they have data (important for filtered views)
        if (userRow.total > 0) {
          floorUsers.push(userRow);
        }
      }
    }
    
    return floorUsers;
  };
  
  const floorUsers = getFloorData().filter(user => !hiddenUsers.has(user.username));
  
  // Helper function to convert color name to CSS
  const getColorStyle = (color) => {
    if (!color) return {};
    
    const colorMap = {
      red: 'rgba(220, 38, 38, 0.3)',
      orange: 'rgba(249, 115, 22, 0.3)',
      green: 'rgba(34, 197, 94, 0.3)',
      purple: 'rgba(168, 85, 247, 0.3)'
    };
    
    return { backgroundColor: colorMap[color] || 'transparent' };
  };
  
  return (
    <div className="floor-table-container">
      <h2 className="floor-title">{floorName}</h2>
      <div className="table-wrapper">
        <table className="floor-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              {HOURS.map(hour => (
                <th key={hour}>{hour}</th>
              ))}
              <th>Total</th>
              {type === "picking" && <th>Items Picked</th>}
              {type === "picking" && <th>Ratio</th>}
              <th>Hours Worked</th>
              <th>Productivity</th>
            </tr>
          </thead>
          <tbody>
            {floorUsers.length === 0 ? (
              <tr>
                <td colSpan={HOURS.length + 4}>No data available</td>
              </tr>
            ) : (
              floorUsers.map((user, index) => (
                <tr 
                  key={index}
                  onClick={() => onToggleUser && onToggleUser(user.username)}
                  style={{ cursor: onToggleUser ? 'pointer' : 'default' }}
                  title={onToggleUser ? 'Click to hide user' : ''}
                >
                  <td>{user.username}</td>
                  <td>{user.name}</td>
                  {HOURS.map(hour => (
                    <td 
                      key={hour}
                      style={getColorStyle(user.hourColors[hour])}
                    >
                      {user.hourCounts[hour] || ''}
                    </td>
                  ))}
                  <td><strong>{user.total}</strong></td>
                  {type === "picking" && (
                    <>
                      <td>{user.items_picked}</td>
                      <td>{user.ratio.toFixed(2)}</td>
                    </>
                  )}
                  <td>{user.hoursWorked.toFixed(2)}</td>
                  <td style={getColorStyle(user.productivityColor)}>
                    {user.productivity.toFixed(2)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FloorTable;

