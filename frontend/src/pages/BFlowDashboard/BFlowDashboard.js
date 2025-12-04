import { useState, useEffect } from 'react';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner';
import HorizontalBarChart from '../../components/charts/HorizontalBarChart';
import { fetchDeliveriesPast, fetchDeliveriesToday, fetchDeliveriesFuture, fetchHuPast, fetchHuToday, fetchHuFuture } from '../../services/api';
import './BFlowDashboard.css';

function BFlowDashboard() {
  const [pastData, setPastData] = useState(null);
  const [todayData, setTodayData] = useState(null);
  const [futureData, setFutureData] = useState(null);
  const [huPastData, setHuPastData] = useState(null);
  const [huTodayData, setHuTodayData] = useState(null);
  const [huFutureData, setHuFutureData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [past, today, future, huPast, huToday, huFuture] = await Promise.all([
          fetchDeliveriesPast(),
          fetchDeliveriesToday(),
          fetchDeliveriesFuture(),
          fetchHuPast(),
          fetchHuToday(),
          fetchHuFuture()
        ]);
        setPastData(past);
        setTodayData(today);
        setFutureData(future);
        setHuPastData(huPast);
        setHuTodayData(huToday);
        setHuFutureData(huFuture);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Process data to calculate sums
  // dataType: 'deliveries' or 'hu' - determines which field names to use
  const processData = (data, includePgi = false, dataType = 'deliveries') => {
    if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
      return {
        notReleased: 0,
        notPicked: 0,
        picked: 0,
        ...(includePgi && { pgi: 0 })
      };
    }

    let notReleased = 0;
    let notPicked = 0;
    let picked = 0;
    let pgi = 0;

    // Determine field names based on data type
    const amountField = dataType === 'hu' ? 'amount_of_hu' : 'amount_of_deliveries';
    const pgidField = dataType === 'hu' ? 'hu_pgid' : 'deliveries_pgid';

    // Iterate through all dates
    Object.values(data).forEach(dateData => {
      if (dateData && typeof dateData === 'object') {
        // Extract pgid if it exists at the date level
        // (it's the same value for all dates, so we just need to capture it once)
        if (includePgi && typeof dateData[pgidField] === 'number' && pgi === 0) {
          pgi = dateData[pgidField];
        }
        
        // Iterate through all hours (skip pgid key)
        Object.entries(dateData).forEach(([key, hourData]) => {
          // Skip pgid key as it's not an hour
          if (key === pgidField) {
            return;
          }
          
          if (hourData && typeof hourData === 'object') {
            // Handle 0 values as well, not just truthy values
            const notReleasedVal = hourData.not_released?.[amountField];
            const notPickedVal = hourData.not_picked?.[amountField];
            const pickedVal = hourData.picked?.[amountField];
            
            if (typeof notReleasedVal === 'number') {
              notReleased += notReleasedVal;
            }
            if (typeof notPickedVal === 'number') {
              notPicked += notPickedVal;
            }
            if (typeof pickedVal === 'number') {
              picked += pickedVal;
            }
          }
        });
      }
    });

    const result = {
      notReleased,
      notPicked,
      picked
    };
    
    if (includePgi) {
      result.pgi = pgi;
    }
    
    return result;
  };

  // Process deliveries data
  const pastMetrics = processData(pastData, false, 'deliveries');
  const todayMetrics = processData(todayData, true, 'deliveries'); // Include PGI for today
  const futureMetrics = processData(futureData, false, 'deliveries');

  // Process HU data
  const huPastMetrics = processData(huPastData, false, 'hu');
  const huTodayMetrics = processData(huTodayData, true, 'hu'); // Include PGI for today
  const huFutureMetrics = processData(huFutureData, false, 'hu');

  // Prepare chart data
  const prepareChartData = (metrics, includePgi = false) => {
    const baseData = [
      { name: 'Not Released', value: metrics.notReleased },
      { name: 'Not Picked', value: metrics.notPicked },
      { name: 'Not PGI', value: metrics.picked }
    ];
    
    if (includePgi && typeof metrics.pgi === 'number') {
      baseData.push({ name: 'PGI', value: metrics.pgi });
    }
    
    return baseData;
  };

  // Deliveries chart data
  const pastChartData = prepareChartData(pastMetrics);
  const todayChartData = prepareChartData(todayMetrics, true); // Include PGI for today
  const futureChartData = prepareChartData(futureMetrics);

  // HU chart data
  const huPastChartData = prepareChartData(huPastMetrics);
  const huTodayChartData = prepareChartData(huTodayMetrics, true); // Include PGI for today
  const huFutureChartData = prepareChartData(huFutureMetrics);

  // Calculate max values for each chart to set proper domain
  const getMaxValue = (chartData) => {
    const max = Math.max(...chartData.map(d => d.value));
    return max > 0 ? Math.ceil(max * 1.1) : 10; // Add 10% padding, minimum 10
  };

  // Deliveries max values
  const pastMax = getMaxValue(pastChartData);
  const todayMax = getMaxValue(todayChartData);
  const futureMax = getMaxValue(futureChartData);

  // HU max values
  const huPastMax = getMaxValue(huPastChartData);
  const huTodayMax = getMaxValue(huTodayChartData);
  const huFutureMax = getMaxValue(huFutureChartData);

  // Colors for bars (4 colors to support PGI bar)
  const colors = ['#ebe9ff', '#a8a5ff', '#7c78ff', '#5a55ff'];

  if (loading) {
    return (
      <PageLayout>
        <LoadingSpinner message="Loading..." />
      </PageLayout>
    );
  }

  // Ensure we have valid chart data
  if (!pastChartData || !todayChartData || !futureChartData || 
      !huPastChartData || !huTodayChartData || !huFutureChartData) {
    return (
      <PageLayout>
        <div className="bflow-dashboard-container">
          <p style={{ color: '#ebe9ff', textAlign: 'center' }}>Loading chart data...</p>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="bflow-dashboard-container">
        <div className="bflow-columns">
          <div className="bflow-column">
            <h2 className="bflow-column-title">Backlog Deliveries</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={pastChartData}
                colors={colors}
                maxValue={pastMax}
                height={200}
              />
            </div>
          </div>

          <div className="bflow-column">
            <h2 className="bflow-column-title">Today Deliveries</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={todayChartData}
                colors={colors}
                maxValue={todayMax}
                height={240}
              />
            </div>
          </div>

          <div className="bflow-column">
            <h2 className="bflow-column-title">Future Deliveries</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={futureChartData}
                colors={colors}
                maxValue={futureMax}
                height={200}
              />
            </div>
          </div>
        </div>

        <div className="bflow-columns" style={{ marginTop: '40px' }}>
          <div className="bflow-column">
            <h2 className="bflow-column-title">Backlog Handling Units</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={huPastChartData}
                colors={colors}
                maxValue={huPastMax}
                height={200}
              />
            </div>
          </div>

          <div className="bflow-column">
            <h2 className="bflow-column-title">Today Handling Units</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={huTodayChartData}
                colors={colors}
                maxValue={huTodayMax}
                height={240}
              />
            </div>
          </div>

          <div className="bflow-column">
            <h2 className="bflow-column-title">Future Handling Units</h2>
            <div className="bflow-chart-container">
              <HorizontalBarChart 
                data={huFutureChartData}
                colors={colors}
                maxValue={huFutureMax}
                height={200}
              />
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}

export default BFlowDashboard;

