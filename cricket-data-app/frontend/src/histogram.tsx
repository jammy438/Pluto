import React from "react";
import { Histogram_data } from "./types";

const Histogram: React.FC<{ data: Histogram_data }> = ({ data }) => {
  const { home_frequency, away_frequency, score_range, home_team, away_team } =
    data;

  // Creates bins with ranges instead of individual scores
  const binSize = 10; // Group scores into ranges of 10
  const numBins = Math.ceil((score_range.max - score_range.min) / binSize);

  const bins: { min: number; max: number; label: string }[] = [];
  for (let i = 0; i < numBins; i++) {
    const min = score_range.min + i * binSize;
    const max = Math.min(min + binSize - 1, score_range.max);
    bins.push({
      min,
      max,
      label: `${min}-${max}`,
    });
  }

  // Calculates frequencies for each bin and convert to percentages
  const binData = bins.map((bin) => {
    let homeCount = 0;
    let awayCount = 0;

    for (let score = bin.min; score <= bin.max; score++) {
      homeCount += home_frequency[score.toString()] || 0;
      awayCount += away_frequency[score.toString()] || 0;
    }

    return { ...bin, homeCount, awayCount };
  });

  // Calculate total counts for percentage calculation
  const totalHomeCount = Object.values(home_frequency).reduce(
    (sum, count) => sum + count,
    0
  );
  const totalAwayCount = Object.values(away_frequency).reduce(
    (sum, count) => sum + count,
    0
  );

  // Convert to percentages
  const binDataWithPercentages = binData.map((bin) => ({
    ...bin,
    homePercentage:
      totalHomeCount > 0 ? (bin.homeCount / totalHomeCount) * 100 : 0,
    awayPercentage:
      totalAwayCount > 0 ? (bin.awayCount / totalAwayCount) * 100 : 0,
  }));

  const maxPercentage = Math.max(
    ...binDataWithPercentages.map((bin) =>
      Math.max(bin.homePercentage, bin.awayPercentage)
    )
  );

  const barWidth = 40;
  const barGap = 10;
  const chartHeight = 300;
  const leftMargin = 80; // Increased for Y-axis labels
  const rightMargin = 20;
  const chartWidth =
    bins.length * (barWidth * 2 + barGap) + leftMargin + rightMargin;

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

      <div
        style={{
          overflowX: "auto",
          overflowY: "visible",
          width: "100%",
          paddingBottom: "20px",
        }}
      >
        <svg
          width={chartWidth}
          height={chartHeight + 130}
          className="histogram-svg"
          style={{ minWidth: `${chartWidth}px` }}
        >
          {/* Y-axis scale lines and labels */}
          {(() => {
            const numTicks = 5;
            const maxRounded = Math.ceil(maxPercentage / 5) * 5; // Round up to nearest 5
            const tickValues = [];
            for (let i = 0; i <= numTicks; i++) {
              tickValues.push((i * maxRounded) / numTicks);
            }

            return tickValues.map((value, i) => {
              const y = chartHeight - (value / maxRounded) * chartHeight + 20;
              return (
                <g key={i}>
                  {/* Grid line */}
                  <line
                    x1={leftMargin - 5}
                    y1={y}
                    x2={chartWidth - rightMargin}
                    y2={y}
                    stroke="#e5e7eb"
                    strokeWidth="1"
                  />
                  {/* Y-axis tick labels */}
                  <text
                    x={leftMargin - 10}
                    y={y + 4}
                    textAnchor="end"
                    fontSize="10"
                    fill="#666"
                  >
                    {value.toFixed(0)}
                  </text>
                </g>
              );
            });
          })()}

          {binDataWithPercentages.map((bin, index) => {
            const maxRounded = Math.ceil(maxPercentage / 5) * 5;
            const homeHeight =
              maxRounded > 0
                ? (bin.homePercentage / maxRounded) * chartHeight
                : 0;
            const awayHeight =
              maxRounded > 0
                ? (bin.awayPercentage / maxRounded) * chartHeight
                : 0;

            const x = index * (barWidth * 2 + barGap) + leftMargin;

            return (
              <g key={bin.label}>
                {/* Home team bar */}
                <rect
                  x={x}
                  y={chartHeight - homeHeight + 20}
                  width={barWidth}
                  height={homeHeight}
                  fill="#3b82f6"
                  className="histogram-bar home"
                />
                {/* Away team bar */}
                <rect
                  x={x + barWidth}
                  y={chartHeight - awayHeight + 20}
                  width={barWidth}
                  height={awayHeight}
                  fill="#ef4444"
                  className="histogram-bar away"
                />
                {/* Score range label */}
                <text
                  x={x + barWidth}
                  y={chartHeight + 60}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#666"
                  transform={`rotate(-45, ${x + barWidth}, ${
                    chartHeight + 60
                  })`}
                >
                  {bin.label}
                </text>
                {/* Home count label */}
                {bin.homeCount > 0 && (
                  <text
                    x={x + barWidth / 2}
                    y={chartHeight - homeHeight + 15}
                    textAnchor="middle"
                    fontSize="10"
                    fill="white"
                  >
                    {bin.homeCount}
                  </text>
                )}
                {/* Away count label */}
                {bin.awayCount > 0 && (
                  <text
                    x={x + barWidth + barWidth / 2}
                    y={chartHeight - awayHeight + 15}
                    textAnchor="middle"
                    fontSize="10"
                    fill="white"
                  >
                    {bin.awayCount}
                  </text>
                )}
              </g>
            );
          })}

          {/* Y-axis label */}
          <text
            x={20}
            y={chartHeight / 2 + 20}
            textAnchor="middle"
            fontSize="12"
            fill="#666"
            transform={`rotate(-90, 20, ${chartHeight / 2 + 20})`}
          >
            Percentage of Matches
          </text>

          {/* X-axis label */}
          <text
            x={
              leftMargin +
              ((bins.length - 1) * (barWidth * 2 + barGap) + barWidth * 2) / 2
            }
            y={chartHeight + 100}
            textAnchor="middle"
            fontSize="12"
            fill="#666"
          >
            Score Range
          </text>
        </svg>
      </div>
    </div>
  );
};

export default Histogram;
