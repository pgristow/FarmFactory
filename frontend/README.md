# FarmFactory Frontend

React-based frontend application for the FarmFactory farm optimization system.

## Tech Stack

- **React 18+** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - UI component library
- **React Router** - Routing
- **React Query** - Data fetching and caching
- **Recharts** - Data visualization
- **React-Leaflet** - Map integration
- **Axios** - HTTP client
- **date-fns** - Date handling

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable components
│   │   │   ├── Card.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   └── layout/          # Layout components
│   │       ├── Layout.tsx
│   │       ├── Sidebar.tsx
│   │       └── Header.tsx
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Farms.tsx
│   │   ├── Plots.tsx
│   │   └── NotFound.tsx
│   ├── services/            # API services
│   │   ├── api.ts
│   │   ├── farmService.ts
│   │   └── plotService.ts
│   ├── types/               # TypeScript types
│   │   ├── farm.ts
│   │   └── api.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Features

### Current Features

- **Dashboard**: Overview of farm statistics and metrics
- **Farm Management**: Create, read, update, and delete farms
- **Plot Management**: Manage plots with farm association
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Comprehensive error boundaries
- **Loading States**: User-friendly loading indicators

### Coming Soon

- Irrigation management dashboard
- Nutrient management dashboard
- Financial tracking and reporting
- Analytics and insights
- Data visualization with charts
- Map-based plot visualization
- Real-time alerts and notifications

## API Integration

The frontend connects to the FastAPI backend at the URL specified in `VITE_API_URL`.

All API calls are handled through service modules:
- `farmService.ts` - Farm-related operations
- `plotService.ts` - Plot-related operations

## Development Notes

- Uses React Query for efficient data fetching and caching
- Material-UI components follow consistent theming
- TypeScript strict mode enabled for type safety
- Vite proxy configured for API requests during development
