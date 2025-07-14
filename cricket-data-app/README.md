# Cricket Simulation Analysis App

A full-stack web application for analysing cricket game simulations and win probabilities. The app displays interactive histograms showing score distributions and calculates win percentages based on simulation data.

## Features

- **Game Selection**: Dropdown interface to select cricket matches
- **Win Probability Analysis**: Displays home team win percentage based on simulation data
- **Interactive Histograms**: Visual representation of score distributions with percentage-based Y-axis
- **Team Performance Comparison**: Side-by-side comparison of home vs away team performance
- **Venue Information**: Shows match venue details
- **Responsive Design**: Clean, modern interface that works on different screen sizes

## Tech Stack

### Backend

- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database for data storage
- **Pandas** - Data manipulation and CSV processing
- **Uvicorn** - ASGI server for running the API

### Frontend

- **React** - JavaScript library for building user interfaces
- **TypeScript** - Type-safe JavaScript
- **CSS3** - Custom styling with modern design
- **SVG** - Custom histogram charts

## Project Structure

```
cricket-data-app/
├── backend/
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── requirements-test.txt # Test dependencies
│   ├── pytest.ini         # Pytest configuration
│   ├── conftest.py         # Pytest fixtures
│   ├── tests/              # Test directory
│   │   ├── __init__.py     # Empty file
│   │   └── test_main.py    # Backend tests
│   ├── data/               # CSV data files
│   │   ├── games.csv       # Match information
│   │   ├── venues.csv      # Venue details
│   │   └── simulations.csv # Team simulation results
│   └── cricket_data.db     # SQLite database (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main application component
│   │   ├── App.test.tsx    # App component tests
│   │   ├── App.css         # Application styles
│   │   ├── histogram.tsx   # Histogram chart component
│   │   ├── histogram.test.tsx # Histogram tests
│   │   ├── gameInfo.tsx    # Game analysis component
│   │   ├── gameInfo.test.tsx # GameInfo tests
│   │   ├── apiService.ts   # API communication layer
│   │   ├── apiService.test.ts # API service tests
│   │   ├── types.ts        # TypeScript type definitions
│   │   ├── setupTests.ts   # Test configuration
│   │   ├── __mocks__/      # Test mocks
│   │   │   └── apiService.ts # API service mock
│   │   └── index.tsx       # Application entry point
│   │   └── index.css       # Base styles
│   ├── public/
│   │   ├── Index.html      # Main HTML template
│   └── package.json        # Node.js dependencies
└── README.md
```

## Installation & Setup

### Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Install test dependencies:

```bash
pip install -r requirements-test.txt
```

5. Create the data directory and add your CSV files:

```bash
mkdir data
# Copy your games.csv, venues.csv, and simulations.csv files to the data/ directory
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

## How to Run the App

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

Frontend will open automatically at `http://localhost:3000`

### Access the Application

Open your browser and go to `http://localhost:3000` to use the app.

**Note**: You need both servers running simultaneously for the app to work properly.

## Running Tests

### Backend Tests

1. Navigate to the backend directory and activate virtual environment:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run all tests:

```bash
pytest
```

3. Run tests with coverage:

```bash
pytest --cov=main --cov-report=html
```

4. Run specific test file:

```bash
pytest tests/test_main.py
```

5. Run tests with verbose output:

```bash
pytest -v
```

### Frontend Tests

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Run all tests:

```bash
npm test
```

3. Run tests with coverage:

```bash
npm run test:coverage
```

4. Run tests in CI mode (no watch):

```bash
npm run test:ci
```

5. Run specific test file:

```bash
npm test App.test.tsx
```

6. Run tests in watch mode:

```bash
npm run test:watch
```

### Test Coverage

Both backend and frontend are configured with 80% coverage thresholds. Coverage reports are generated in HTML format for detailed analysis.

## Data Format

### games.csv

```csv
home_team,away_team,date,venue_id
Doncaster Renegades,Hull Stars,2024-03-24,2
Oldham Super Kings,Rochdale Hurricanes,2024-04-04,2
```

### venues.csv

```csv
venue_id,venue_name
0,Morecambe International Cricket Ground
1,Lady's
2,The Square
```

### simulations.csv

```csv
team_id,team,simulation_run,results
0,Peterborough Strikers,1,141
0,Peterborough Strikers,2,154
1,Huddersfield Heat,1,160
```

## API Endpoints

### Base URL: `http://localhost:8000`

- **GET /games** - Retrieve all games with venue information
- **GET /venues** - Retrieve all venues
- **GET /games/{game_id}/analysis** - Get game analysis with win probabilities
- **GET /games/{game_id}/histogram-data** - Get histogram data for visualization

## Usage

1. **Start both servers** (backend on :8000, frontend on :3000)
2. **Select a game** from the dropdown menu
3. **View analysis** including:
   - Team matchup details
   - Venue information
   - Home team win percentage
   - Total number of simulations
4. **Explore the histogram** showing score distribution percentages
5. **Compare team performance** through side-by-side bar charts

## Key Features Explained

### Win Probability Calculation

The app calculates win probabilities by comparing simulation results between home and away teams. For each game, it takes the simulation scores for both teams and determines how often the home team's score exceeds the away team's score.

### Histogram Visualization

- **Binning**: Scores are grouped into 10-point ranges (e.g., 120-129, 130-139)
- **Percentage-based**: Y-axis shows percentage of matches rather than raw frequency
- **Color-coded**: Blue bars for home team, red bars for away team
- **Responsive scaling**: Y-axis automatically adjusts to data range

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create new components in the `src/` directory
3. **Types**: Update TypeScript interfaces in `types.ts`
4. **Styling**: Modify `App.css` for visual changes

### Testing Guidelines

1. **Write tests for new features** - All new components and API endpoints should include tests
2. **Maintain coverage** - Keep test coverage above 80%
3. **Test edge cases** - Include tests for error conditions and boundary cases
4. **Use mocks appropriately** - Mock external dependencies in tests
5. **Run tests before commits** - Ensure all tests pass before pushing changes

### Database Schema

The app automatically creates SQLite tables from CSV data:

- **venues**: venue_id, venue_name
- **games**: id, home_team, away_team, date, venue_id
- **simulations**: id, team_id, team, simulation_run, results

## Troubleshooting

### Common Issues

**CORS Errors**

- Ensure the frontend is running on port 3000
- Check CORS settings in `main.py`

**Data Not Loading**

- Verify CSV files are in the `backend/data/` directory
- Check file names match exactly: `games.csv`, `venues.csv`, `simulations.csv`
- Ensure CSV headers are correct

**Histogram Not Displaying**

- Check browser console for JavaScript errors
- Verify simulation data exists for both teams
- Ensure team names match between games.csv and simulations.csv

**API Connection Issues**

- Confirm backend is running on `http://localhost:8000`
- Check `apiService.ts` has correct API base URL
- Verify no firewall blocking ports 3000 or 8000

**Test Failures**

- Ensure all dependencies are installed (`requirements-test.txt` for backend, test packages for frontend)
- Check that test database permissions are correct
- Verify mock configurations are properly set up

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. **Run tests** to ensure existing functionality works (`pytest` for backend, `npm test` for frontend)
4. **Add tests** for your new feature
5. **Ensure test coverage** remains above 80%
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request