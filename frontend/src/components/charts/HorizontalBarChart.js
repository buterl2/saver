import React from 'react';
import './HorizontalBarChart.css';

function HorizontalBarChart({ data, colors, maxValue, height = 200 }) {
  if (!data || data.length === 0) {
    return (
      <div className="horizontal-bar-chart" style={{ height: `${height}px` }}>
        <p style={{ color: '#ebe9ff', textAlign: 'center', padding: '20px' }}>No data available</p>
      </div>
    );
  }

  const chartHeight = height;
  const chartWidth = 500;
  const totalSpacing = 60;
  const availableHeight = chartHeight - totalSpacing;
  const barHeight = 30;
  const spacing = availableHeight > barHeight * data.length 
    ? (availableHeight - barHeight * data.length) / (data.length + 1)
    : 10;
  const labelWidth = 110;
  const barAreaWidth = chartWidth - labelWidth - 60;
  const maxBarWidth = barAreaWidth;

  return (
    <div className="horizontal-bar-chart" style={{ height: `${chartHeight}px`, width: '100%' }}>
      <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="xMidYMid meet">
        {data.map((item, index) => {
          const barWidth = maxValue > 0 ? (item.value / maxValue) * maxBarWidth : 0;
          const barY = 30 + index * (barHeight + spacing);
          
          return (
            <g key={index}>
              <text
                x={labelWidth - 10}
                y={barY + 20}
                fill="#ebe9ff"
                fontSize="13"
                textAnchor="end"
                className="bar-label"
              >
                {item.name}
              </text>
              <rect
                x={labelWidth}
                y={barY}
                width={barWidth}
                height={barHeight}
                fill={colors[index % colors.length]}
                rx={4}
                className="bar-rect"
              />
              <text
                x={labelWidth + barWidth + 8}
                y={barY + 20}
                fill="#ebe9ff"
                fontSize="12"
                className="bar-value"
              >
                {item.value}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default HorizontalBarChart;
