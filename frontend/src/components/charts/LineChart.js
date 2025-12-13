import React from 'react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import './LineChart.css';

function LineChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return (
      <div className="line-chart-container" style={{ height: `${height}px` }}>
        <p className="line-chart-no-data">No data available</p>
      </div>
    );
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="line-chart-tooltip">
          <p className="line-chart-tooltip-label">{data.time}</p>
          <p className="line-chart-tooltip-value">
            {data.lines_picked.toLocaleString()} lines
          </p>
          {data.lines_per_hour !== undefined && (
            <p className="line-chart-tooltip-rate">
              {data.lines_per_hour > 0 ? '+' : ''}{data.lines_per_hour.toLocaleString()} lines/hour
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="line-chart-container" style={{ height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis 
            dataKey="time" 
            stroke="#a8a5d6"
            tick={{ fill: '#a8a5d6', fontSize: 12, fontFamily: 'Montserrat' }}
            tickLine={{ stroke: '#a8a5d6' }}
          />
          <YAxis 
            yAxisId="left"
            stroke="#a8a5d6"
            tick={{ fill: '#a8a5d6', fontSize: 12, fontFamily: 'Montserrat' }}
            tickLine={{ stroke: '#a8a5d6' }}
            width={60}
            label={{ value: 'Lines Picked', angle: -90, position: 'insideLeft', fill: '#a8a5d6', style: { fontFamily: 'Montserrat' } }}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            stroke="#ffa94d"
            tick={{ fill: '#ffa94d', fontSize: 12, fontFamily: 'Montserrat' }}
            tickLine={{ stroke: '#ffa94d' }}
            width={60}
            label={{ value: 'Lines/Hour', angle: 90, position: 'insideRight', fill: '#ffa94d', style: { fontFamily: 'Montserrat' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontFamily: 'Montserrat', color: '#ebe9ff' }}
            iconType="line"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="lines_picked" 
            stroke="#7c78ff" 
            strokeWidth={2}
            dot={{ fill: '#7c78ff', r: 4 }}
            activeDot={{ r: 6, fill: '#ebe9ff' }}
            name="Lines Picked"
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="lines_per_hour" 
            stroke="#ffa94d" 
            strokeWidth={2}
            dot={{ fill: '#ffa94d', r: 3 }}
            activeDot={{ r: 5, fill: '#ffa94d' }}
            strokeDasharray="5 5"
            name="Rate (lines/hour)"
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default LineChart;

