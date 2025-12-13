import { useState, useEffect, useMemo } from 'react';
import { TbArrowUp, TbArrowDown, TbMinus } from 'react-icons/tb';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner';
import { 
  fetchDeliveriesDashboard, 
  fetchDeliveriesPgiDashboard,
  fetchHuDashboard,
  fetchHuPgiDashboard,
  fetchLinesDashboard,
  fetchLinesPgiDashboard,
  fetchLinesHourlyDashboard
} from '../../services/api';
import LineChart from '../../components/charts/LineChart';
import { AVERAGE_RATIOS } from '../../utils/constants';
import './BFlowDashboard.css';

// Floor options
const FLOOR_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'ground_floor', label: 'Ground Floor' },
  { value: 'first_floor', label: 'First Floor' },
  { value: 'second_floor', label: 'Second Floor' },
];

// Date range options
const DATE_RANGE_OPTIONS = [
  { value: 'backlog', label: 'Backlog' },
  { value: 'today', label: 'Today' },
  { value: 'future', label: 'Future' },
];

// Parse date string DD.MM.YYYY to Date object
const parseDate = (dateStr) => {
  const [day, month, year] = dateStr.split('.');
  return new Date(year, month - 1, day);
};

// Get today's date string in DD.MM.YYYY format
const getTodayString = () => {
  const today = new Date();
  const day = String(today.getDate()).padStart(2, '0');
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const year = today.getFullYear();
  return `${day}.${month}.${year}`;
};

// Calculate indicator (percentage, color, arrow) based on current vs average ratio
const calculateIndicator = (currentRatio, averageRatio, isInverted = false) => {
  if (!currentRatio || currentRatio === 0 || !averageRatio || averageRatio === 0) {
    return null;
  }

  const percentageDiff = ((currentRatio - averageRatio) / averageRatio) * 100;
  const absPercentage = Math.abs(percentageDiff);
  
  let color, Icon;
  
  if (absPercentage < 0.1) {
    // Very close to average (within 0.1%)
    color = '#ffa94d'; // orange
    Icon = TbMinus;
  } else {
    const isHigher = percentageDiff > 0;
    
    if (isInverted) {
      // For inverted (HU per delivery): more is bad (red up), less is good (green down)
      if (isHigher) {
        color = '#ff6b6b'; // red
        Icon = TbArrowUp;
      } else {
        color = '#69db7c'; // green
        Icon = TbArrowDown;
      }
    } else {
      // For normal (Lines): more is good (green up), less is bad (red down)
      if (isHigher) {
        color = '#69db7c'; // green
        Icon = TbArrowUp;
      } else {
        color = '#ff6b6b'; // red
        Icon = TbArrowDown;
      }
    }
  }

  return {
    percentage: absPercentage < 0.1 ? 0 : percentageDiff,
    color,
    Icon,
  };
};

// Indicator component
const RatioIndicator = ({ indicator, label }) => {
  if (!indicator) return null;

  const { percentage, color, Icon } = indicator;
  const displayPercentage = Math.abs(percentage).toFixed(1);

  return (
    <div className="bflow-ratio-indicator">
      <div className="bflow-indicator-content" style={{ color }}>
        <span className="bflow-indicator-percentage">
          {percentage > 0 ? '+' : ''}{displayPercentage}%
        </span>
        <Icon className="bflow-indicator-icon" />
      </div>
      <div className="bflow-indicator-label">{label}</div>
    </div>
  );
};

function BFlowDashboard() {
  const [deliveriesData, setDeliveriesData] = useState(null);
  const [deliveriesPgiData, setDeliveriesPgiData] = useState(null);
  const [huData, setHuData] = useState(null);
  const [huPgiData, setHuPgiData] = useState(null);
  const [linesData, setLinesData] = useState(null);
  const [linesPgiData, setLinesPgiData] = useState(null);
  const [linesHourlyData, setLinesHourlyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFloor, setSelectedFloor] = useState('all');
  const [selectedDateRange, setSelectedDateRange] = useState('today');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [deliveries, deliveriesPgi, hu, huPgi, lines, linesPgi, linesHourly] = await Promise.all([
          fetchDeliveriesDashboard(),
          fetchDeliveriesPgiDashboard(),
          fetchHuDashboard(),
          fetchHuPgiDashboard(),
          fetchLinesDashboard(),
          fetchLinesPgiDashboard(),
          fetchLinesHourlyDashboard(),
        ]);
        setDeliveriesData(deliveries);
        setDeliveriesPgiData(deliveriesPgi);
        setHuData(hu);
        setHuPgiData(huPgi);
        setLinesData(lines);
        setLinesPgiData(linesPgi);
        setLinesHourlyData(linesHourly);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Calculate deliveries metrics based on selected floor and date range
  const deliveriesMetrics = useMemo(() => {
    if (!deliveriesData) return { open: 0, notPicked: 0, fullyPicked: 0, pgi: 0 };

    const todayStr = getTodayString();
    const today = parseDate(todayStr);

    let notPicked = 0;
    let fullyPicked = 0;

    // Filter dates based on selected range
    Object.entries(deliveriesData).forEach(([dateStr, dateData]) => {
      const date = parseDate(dateStr);
      
      let includeDate = false;
      if (selectedDateRange === 'backlog' && date < today) {
        includeDate = true;
      } else if (selectedDateRange === 'today' && dateStr === todayStr) {
        includeDate = true;
      } else if (selectedDateRange === 'future' && date > today) {
        includeDate = true;
      }

      if (includeDate && dateData) {
        // Get the right data based on floor selection
        let bData, cData;
        
        if (selectedFloor === 'all') {
          bData = dateData.b;
          cData = dateData.c;
        } else {
          const floorData = dateData[selectedFloor];
          if (floorData) {
            bData = floorData.b;
            cData = floorData.c;
          }
        }

        if (bData && typeof bData.amount_of_deliveries === 'number') {
          notPicked += bData.amount_of_deliveries;
        }
        if (cData && typeof cData.amount_of_deliveries === 'number') {
          fullyPicked += cData.amount_of_deliveries;
        }
      }
    });

    // Get PGI data (only for today)
    let pgi = 0;
    if (selectedDateRange === 'today' && deliveriesPgiData) {
      const todayPgiData = deliveriesPgiData[todayStr];
      if (todayPgiData) {
        if (selectedFloor === 'all') {
          pgi = todayPgiData.amount_of_deliveries_pgi || 0;
        } else {
          const floorPgiData = todayPgiData[selectedFloor];
          if (floorPgiData) {
            pgi = floorPgiData.amount_of_deliveries_pgi || 0;
          }
        }
      }
    }

    return {
      open: notPicked + fullyPicked,
      notPicked,
      fullyPicked,
      pgi,
    };
  }, [deliveriesData, deliveriesPgiData, selectedFloor, selectedDateRange]);

  // Calculate HU metrics based on selected floor and date range
  const huMetrics = useMemo(() => {
    if (!huData) return { open: 0, notPicked: 0, picked: 0, pgi: 0 };

    const todayStr = getTodayString();
    const today = parseDate(todayStr);

    let notPicked = 0;
    let picked = 0;

    // Filter dates based on selected range
    Object.entries(huData).forEach(([dateStr, dateData]) => {
      const date = parseDate(dateStr);
      
      let includeDate = false;
      if (selectedDateRange === 'backlog' && date < today) {
        includeDate = true;
      } else if (selectedDateRange === 'today' && dateStr === todayStr) {
        includeDate = true;
      } else if (selectedDateRange === 'future' && date > today) {
        includeDate = true;
      }

      if (includeDate && dateData) {
        let pickedData, notPickedData;
        
        if (selectedFloor === 'all') {
          pickedData = dateData.picked;
          notPickedData = dateData.not_picked;
        } else {
          const floorData = dateData[selectedFloor];
          if (floorData) {
            pickedData = floorData.picked;
            notPickedData = floorData.not_picked;
          }
        }

        if (pickedData && typeof pickedData.amount_of_hu === 'number') {
          picked += pickedData.amount_of_hu;
        }
        if (notPickedData && typeof notPickedData.amount_of_hu === 'number') {
          notPicked += notPickedData.amount_of_hu;
        }
      }
    });

    // Get PGI data (only for today)
    let pgi = 0;
    if (selectedDateRange === 'today' && huPgiData) {
      const todayPgiData = huPgiData[todayStr];
      if (todayPgiData) {
        if (selectedFloor === 'all') {
          pgi = todayPgiData.amount_of_hu_pgi || 0;
        } else {
          const floorPgiData = todayPgiData[selectedFloor];
          if (floorPgiData) {
            pgi = floorPgiData.amount_of_hu_pgi || 0;
          }
        }
      }
    }

    return {
      open: notPicked + picked,
      notPicked,
      picked,
      pgi,
    };
  }, [huData, huPgiData, selectedFloor, selectedDateRange]);

  // Calculate Lines metrics based on selected floor and date range
  const linesMetrics = useMemo(() => {
    if (!linesData) return { open: 0, notPicked: 0, picked: 0, pgi: 0 };

    const todayStr = getTodayString();
    const today = parseDate(todayStr);

    let notPicked = 0;
    let picked = 0;

    // Filter dates based on selected range
    Object.entries(linesData).forEach(([dateStr, dateData]) => {
      const date = parseDate(dateStr);
      
      let includeDate = false;
      if (selectedDateRange === 'backlog' && date < today) {
        includeDate = true;
      } else if (selectedDateRange === 'today' && dateStr === todayStr) {
        includeDate = true;
      } else if (selectedDateRange === 'future' && date > today) {
        includeDate = true;
      }

      if (includeDate && dateData) {
        let pickedData, notPickedData;
        
        if (selectedFloor === 'all') {
          pickedData = dateData.picked;
          notPickedData = dateData.not_picked;
        } else {
          const floorData = dateData[selectedFloor];
          if (floorData) {
            pickedData = floorData.picked;
            notPickedData = floorData.not_picked;
          }
        }

        if (pickedData && typeof pickedData.amount_of_lines === 'number') {
          picked += pickedData.amount_of_lines;
        }
        if (notPickedData && typeof notPickedData.amount_of_lines === 'number') {
          notPicked += notPickedData.amount_of_lines;
        }
      }
    });

    // Get PGI data (only for today)
    let pgi = 0;
    if (selectedDateRange === 'today' && linesPgiData) {
      const todayPgiData = linesPgiData[todayStr];
      if (todayPgiData) {
        if (selectedFloor === 'all') {
          pgi = todayPgiData.amount_of_lines_pgi || 0;
        } else {
          const floorPgiData = todayPgiData[selectedFloor];
          if (floorPgiData) {
            pgi = floorPgiData.amount_of_lines_pgi || 0;
          }
        }
      }
    }

    return {
      open: notPicked + picked,
      notPicked,
      picked,
      pgi,
    };
  }, [linesData, linesPgiData, selectedFloor, selectedDateRange]);

  // Calculate indicators
  const huPerDeliveryIndicator = useMemo(() => {
    if (deliveriesMetrics.open === 0 || huMetrics.open === 0) return null;
    const currentRatio = huMetrics.open / deliveriesMetrics.open;
    return calculateIndicator(currentRatio, AVERAGE_RATIOS.HU_PER_DELIVERY, true);
  }, [deliveriesMetrics.open, huMetrics.open]);

  const linesPerHuIndicator = useMemo(() => {
    if (huMetrics.open === 0 || linesMetrics.open === 0) return null;
    const currentRatio = linesMetrics.open / huMetrics.open;
    return calculateIndicator(currentRatio, AVERAGE_RATIOS.LINES_PER_HU, false);
  }, [huMetrics.open, linesMetrics.open]);

  const linesPerDeliveryIndicator = useMemo(() => {
    if (deliveriesMetrics.open === 0 || linesMetrics.open === 0) return null;
    const currentRatio = linesMetrics.open / deliveriesMetrics.open;
    return calculateIndicator(currentRatio, AVERAGE_RATIOS.LINES_PER_DELIVERY, false);
  }, [deliveriesMetrics.open, linesMetrics.open]);

  // Process hourly data for chart
  const chartData = useMemo(() => {
    if (!linesHourlyData) return [];

    const todayStr = getTodayString();
    const today = parseDate(todayStr);

    // Check if data is organized by date (has date keys like "DD.MM.YYYY")
    // or if it's flat (directly has time slot keys like "0700")
    const firstKey = Object.keys(linesHourlyData)[0];
    const isDateOrganized = firstKey && firstKey.includes('.');

    let filteredData = {};

    if (isDateOrganized) {
      // Data is organized by date
      Object.entries(linesHourlyData).forEach(([dateStr, dateData]) => {
        const date = parseDate(dateStr);
        
        let includeDate = false;
        if (selectedDateRange === 'backlog' && date < today) {
          includeDate = true;
        } else if (selectedDateRange === 'today' && dateStr === todayStr) {
          includeDate = true;
        } else if (selectedDateRange === 'future' && date > today) {
          includeDate = true;
        }

        if (includeDate && dateData) {
          // Get data based on floor selection
          let hourlyData = {};
          
          if (selectedFloor === 'all') {
            hourlyData = dateData;
          } else {
            const floorData = dateData[selectedFloor];
            if (floorData) {
              hourlyData = floorData;
            }
          }

          // Aggregate hourly data across all dates
          Object.entries(hourlyData).forEach(([timeSlot, slotData]) => {
            if (slotData && typeof slotData.lines_picked === 'number') {
              if (!filteredData[timeSlot]) {
                filteredData[timeSlot] = 0;
              }
              filteredData[timeSlot] += slotData.lines_picked;
            }
          });
        }
      });
    } else {
      // Data is flat - use directly (works for all filters as user mentioned)
      Object.entries(linesHourlyData).forEach(([timeSlot, slotData]) => {
        if (slotData && typeof slotData.lines_picked === 'number') {
          filteredData[timeSlot] = slotData.lines_picked;
        }
      });
    }

    // Convert to array and format time slots
    const timeSlots = Object.keys(filteredData).sort();
    const chartData = timeSlots.map((timeSlot, index) => {
      // Shift time by 30 minutes: 0700 -> 07:30, 0730 -> 08:00, etc.
      const hours = parseInt(timeSlot.substring(0, 2));
      const minutes = parseInt(timeSlot.substring(2, 4));
      
      // Add 30 minutes
      let newHours = hours;
      let newMinutes = minutes + 30;
      if (newMinutes >= 60) {
        newHours += 1;
        newMinutes -= 60;
      }
      if (newHours >= 24) {
        newHours -= 24;
      }
      
      const formattedTime = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`;
      
      return {
        time: formattedTime,
        timeSlot: timeSlot,
        lines_picked: filteredData[timeSlot],
        originalTime: `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
      };
    });

    // Calculate rate (lines per hour) - derivative
    // Since each data point represents 30 minutes, we calculate the rate between consecutive points
    const chartDataWithRate = chartData.map((point, index) => {
      let rate = 0;
      
      if (index > 0) {
        // Calculate rate: difference between current and previous point
        // Since each point is 30 minutes, multiply by 2 to get per hour
        const timeDiff = 0.5; // 30 minutes = 0.5 hours
        const linesDiff = point.lines_picked - chartData[index - 1].lines_picked;
        rate = linesDiff / timeDiff; // lines per hour
      } else {
        // For first point, use the next point's rate or 0
        if (chartData.length > 1) {
          const timeDiff = 0.5;
          const linesDiff = chartData[1].lines_picked - point.lines_picked;
          rate = linesDiff / timeDiff;
        }
      }
      
      return {
        ...point,
        lines_per_hour: Math.round(rate)
      };
    });

    return chartDataWithRate;
  }, [linesHourlyData, selectedFloor, selectedDateRange]);

  if (loading) {
    return (
      <PageLayout>
        <LoadingSpinner message="Loading..." />
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="bflow-dashboard-container">
        {/* Controls */}
        <div className="bflow-controls">
          <div className="bflow-dropdown-group">
            <label className="bflow-dropdown-label">Floor</label>
            <select
              className="bflow-dropdown"
              value={selectedFloor}
              onChange={(e) => setSelectedFloor(e.target.value)}
            >
              {FLOOR_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="bflow-dropdown-group">
            <label className="bflow-dropdown-label">Period</label>
            <select
              className="bflow-dropdown"
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value)}
            >
              {DATE_RANGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Main Card - Split into 3 sections */}
        <div className="bflow-main-card">
          {/* Left Section - Deliveries */}
          <div className="bflow-section bflow-section-left">
            <h3 className="bflow-section-title">Deliveries</h3>
            <div className="bflow-metric-main">
              <span className="bflow-metric-number">{deliveriesMetrics.open.toLocaleString()}</span>
              <span className="bflow-metric-label">Open Deliveries</span>
            </div>
            <div className="bflow-metric-columns">
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Not Picked</div>
                <div className="bflow-column-value bflow-not-picked">{deliveriesMetrics.notPicked.toLocaleString()}</div>
              </div>
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Picked</div>
                <div className="bflow-column-value bflow-fully-picked">{deliveriesMetrics.fullyPicked.toLocaleString()}</div>
              </div>
            </div>
            {selectedDateRange === 'today' && (
              <div className="bflow-metric-pgi">
                <span className="bflow-pgi-number">{deliveriesMetrics.pgi.toLocaleString()}</span> deliveries PGI
              </div>
            )}
          </div>

          {/* Separator */}
          <div className="bflow-separator"></div>

          {/* Middle Section - Handling Units */}
          <div className="bflow-section bflow-section-middle">
            <h3 className="bflow-section-title">Handling Units</h3>
            <div className="bflow-metric-main">
              <div className="bflow-metric-number-container">
                <span className="bflow-metric-number">{huMetrics.open.toLocaleString()}</span>
                <RatioIndicator 
                  indicator={huPerDeliveryIndicator} 
                  label="vs deliveries"
                />
              </div>
              <span className="bflow-metric-label">Open Handling Units</span>
            </div>
            <div className="bflow-metric-columns">
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Not Picked</div>
                <div className="bflow-column-value bflow-not-picked">{huMetrics.notPicked.toLocaleString()}</div>
              </div>
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Picked</div>
                <div className="bflow-column-value bflow-fully-picked">{huMetrics.picked.toLocaleString()}</div>
              </div>
            </div>
            {selectedDateRange === 'today' && (
              <div className="bflow-metric-pgi">
                <span className="bflow-pgi-number">{huMetrics.pgi.toLocaleString()}</span> handling units PGI
              </div>
            )}
          </div>

          {/* Separator */}
          <div className="bflow-separator"></div>

          {/* Right Section - Lines */}
          <div className="bflow-section bflow-section-right">
            <h3 className="bflow-section-title">Lines</h3>
            <div className="bflow-metric-main">
              <div className="bflow-metric-number-container">
                <span className="bflow-metric-number">{linesMetrics.open.toLocaleString()}</span>
                <div className="bflow-indicators-group">
                  <RatioIndicator 
                    indicator={linesPerHuIndicator} 
                    label="vs HU"
                  />
                  <RatioIndicator 
                    indicator={linesPerDeliveryIndicator} 
                    label="vs deliveries"
                  />
                </div>
              </div>
              <span className="bflow-metric-label">Open Lines</span>
            </div>
            <div className="bflow-metric-columns">
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Not Picked</div>
                <div className="bflow-column-value bflow-not-picked">{linesMetrics.notPicked.toLocaleString()}</div>
              </div>
              <div className="bflow-metric-column">
                <div className="bflow-column-label">Not PGI</div>
                <div className="bflow-column-value bflow-fully-picked">{linesMetrics.picked.toLocaleString()}</div>
              </div>
            </div>
            {selectedDateRange === 'today' && (
              <div className="bflow-metric-pgi">
                <span className="bflow-pgi-number">{linesMetrics.pgi.toLocaleString()}</span> lines PGI
              </div>
            )}
          </div>
        </div>

        {/* Hourly Chart Card */}
        <div className="bflow-chart-card">
          <h3 className="bflow-chart-title">Lines Picked by Time</h3>
          <LineChart data={chartData} height={300} />
        </div>
      </div>
    </PageLayout>
  );
}

export default BFlowDashboard;
