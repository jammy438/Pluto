import React from "react";
import { Histogram_data } from "./types";

const Histogram: React.FC<{ data: Histogram_data }> = ({ data }) => {
  const { home_frequency, away_frequency, score_range, home_team, away_team } =
    data;

  const bins: number[] = [];
  for (let i = score_range.min; i <= score_range.max; i++) {
    bins.push(i);
  }

  const maxFreq = Math.max(
    ...Object.values(home_frequency),
    ...Object.values(away_frequency)
  );

  const barWidth = 40;
  const barGap = 2;
  const chartHeight = 300;
  const chartWidth = bins.length * (barWidth * 2 + barGap) + 100;

  return (
    <div className="histogram-container">
      <h3>Simulation Results Distribution</h3>
      <div className="histogram-legend">
        <div className="legend-item">
          <div className="legend-color home"></div>
          <span>{home_team} (Home)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color away"></div>
          <span>{away_team} (Away)</span>
        </div>
      </div>

      <svg
        width={chartWidth}
        height={chartHeight + 50}
        className="histogram-svg"
      >
        {bins.map((score, index) => {
          const homeCount = home_frequency[score] || 0;
          const awayCount = away_frequency[score] || 0;

          const homeHeight = (homeCount / maxFreq) * chartHeight;
          const awayHeight = (awayCount / maxFreq) * chartHeight;

          const x = index * (barWidth * 2 + barGap) + 50;

          return (
            <g key={score}>
              <rect
                x={x}
                y={chartHeight - homeHeight + 20}
                width={barWidth}
                height={homeHeight}
                fill="#3b82f6"
                className="histogram-bar home"
              />
              <rect
                x={x + barWidth}
                y={chartHeight - awayHeight + 20}
                width={barWidth}
                height={awayHeight}
                fill="#ef4444"
                className="histogram-bar away"
              />
              <text
                x={x + barWidth}
                y={chartHeight + 40}
                textAnchor="middle"
                fontSize="12"
                fill="#666"
              >
                {score}
              </text>
              {homeCount > 0 && (
                <text
                  x={x + barWidth / 2}
                  y={chartHeight - homeHeight + 15}
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                >
                  {homeCount}
                </text>
              )}
              {awayCount > 0 && (
                <text
                  x={x + barWidth + barWidth / 2}
                  y={chartHeight - awayHeight + 15}
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                >
                  {awayCount}
                </text>
              )}
            </g>
          );
        })}
        <text
          x={20}
          y={chartHeight / 2}
          textAnchor="middle"
          fontSize="12"
          fill="#666"
          transform={`rotate(-90, 20, ${chartHeight / 2})`}
        >
          Frequency
        </text>
        <text
          x={chartWidth / 2}
          y={chartHeight + 50}
          textAnchor="middle"
          fontSize="12"
          fill="#666"
        >
          Score
        </text>
      </svg>
    </div>
  );
};

export default Histogram;
