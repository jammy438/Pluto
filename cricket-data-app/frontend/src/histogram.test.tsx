// histogram.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Histogram from './histogram';
import { Histogram_data } from './types';

const mockHistogramData: Histogram_data = {
  home_team: 'Team Alpha',
  away_team: 'Team Beta',
  home_scores: [150, 160, 155, 170, 145, 165, 175, 140, 180, 135],
  away_scores: [140, 155, 145, 165, 135, 150, 160, 130, 170, 125],
  home_frequency: { 
    '150': 5, '160': 3, '155': 2, '170': 1, '145': 4,
    '165': 2, '175': 1, '140': 3, '180': 1, '135': 2
  },
  away_frequency: { 
    '140': 4, '155': 4, '145': 2, '165': 2, '135': 3,
    '150': 3, '160': 2, '130': 1, '170': 2, '125': 1
  },
  score_range: { min: 125, max: 180 }
};

const simpleHistogramData: Histogram_data = {
  home_team: 'Simple Home',
  away_team: 'Simple Away',
  home_scores: [150, 151, 152],
  away_scores: [148, 149, 150],
  home_frequency: { '150': 1, '151': 1, '152': 1 },
  away_frequency: { '148': 1, '149': 1, '150': 1 },
  score_range: { min: 148, max: 152 }
};

describe('Histogram Component', () => {
  test('renders histogram title', () => {
    render(<Histogram data={mockHistogramData} />);
    
    expect(screen.getByText('Simulation Results Distribution')).toBeInTheDocument();
  });

  test('renders legend with correct team names', () => {
    render(<Histogram data={mockHistogramData} />);
    
    expect(screen.getByText('Team Alpha (Home)')).toBeInTheDocument();
    expect(screen.getByText('Team Beta (Away)')).toBeInTheDocument();
  });

  test('renders legend with colored indicators', () => {
    render(<Histogram data={mockHistogramData} />);
    
    const homeLegendColor = document.querySelector('.legend-color.home');
    const awayLegendColor = document.querySelector('.legend-color.away');
    
    expect(homeLegendColor).toBeInTheDocument();
    expect(awayLegendColor).toBeInTheDocument();
  });

  test('renders SVG histogram element', () => {
    render(<Histogram data={mockHistogramData} />);
    
    const svg = document.querySelector('svg.histogram-svg');
    expect(svg).toBeInTheDocument();
  });

  test('creates histogram bars', () => {
    render(<Histogram data={mockHistogramData} />);
    
    const homeBars = document.querySelectorAll('.histogram-bar.home');
    const awayBars = document.querySelectorAll('.histogram-bar.away');
    
    expect(homeBars.length).toBeGreaterThan(0);
    expect(awayBars.length).toBeGreaterThan(0);
  });

  test('bars have correct home and away classes', () => {
    render(<Histogram data={mockHistogramData} />);
    
    const homeBars = document.querySelectorAll('rect.histogram-bar.home');
    const awayBars = document.querySelectorAll('rect.histogram-bar.away');
    
    expect(homeBars.length).toBeGreaterThan(0);
    expect(awayBars.length).toBeGreaterThan(0);
    
    // Checks that bars have correct fill colors via CSS classes
    homeBars.forEach(bar => {
      expect(bar).toHaveClass('home');
    });
    
    awayBars.forEach(bar => {
      expect(bar).toHaveClass('away');
    });
  });

  test('renders Y-axis labels', () => {
    render(<Histogram data={mockHistogramData} />);
    
    // Checks for percentage labels on Y-axis
    const yAxisLabels = document.querySelectorAll('text[text-anchor="end"]');
    expect(yAxisLabels.length).toBeGreaterThan(0);
  });

  test('renders X-axis score range labels', () => {
    render(<Histogram data={mockHistogramData} />);
    
    // Check for score range labels (they should be rotated text elements)
    const xAxisLabels = document.querySelectorAll('text[transform*="rotate(-45"]');
    expect(xAxisLabels.length).toBeGreaterThan(0);
  });

  test('renders axis titles', () => {
    render(<Histogram data={mockHistogramData} />);
    
    // Check for Y-axis title
    const yAxisTitle = Array.from(document.querySelectorAll('text')).find(
      el => el.textContent === 'Percentage of Matches'
    );
    expect(yAxisTitle).toBeInTheDocument();
    
    // Check for X-axis title
    const xAxisTitle = Array.from(document.querySelectorAll('text')).find(
      el => el.textContent === 'Score Range'
    );
    expect(xAxisTitle).toBeInTheDocument();
  });

  