# FarmFactory - Farm Optimization System

A comprehensive data-driven farm management platform designed to optimize agricultural yields through intelligent data collection, analysis, and decision support.

## Overview

FarmFactory enables farmers to:
- **Import data** from CSV/Excel files (irrigation, nutrients, soil profiles, phenology observations, financials)
- **Store and manage** farm data in a scalable PostgreSQL + TimescaleDB database
- **Monitor in real-time** through interactive dashboards
- **Receive alerts** when variables fall outside optimal ranges
- **Make informed decisions** based on analytics and AI-powered recommendations

## Key Features

### 📊 Data Management
- Multi-source data import (CSV/Excel)
- Intelligent column mapping and validation
- Support for time-series data (irrigation, nutrients, environmental sensors)
- Scalable storage with automatic partitioning

### 🚜 Farm Operations
- Farm and plot location management with GIS support
- Soil profile tracking and analysis
- Crop planting and phenology observations
- Irrigation and nutrient application tracking
- Water quality monitoring

### 💰 Financial Tracking
- Input cost tracking (seeds, fertilizer, water, labor)
- Harvest revenue recording
- Profit & loss analysis by plot and crop
- ROI calculations and cost optimization

### 📈 Analytics & Insights
- Yield prediction using machine learning
- Input efficiency analysis
- Irrigation and nutrient optimization recommendations
- Comparative analysis across plots and seasons
- Trend visualization

### 🔔 Smart Alerts
- Configurable thresholds for all monitored parameters
- Real-time notifications for out-of-spec conditions
- Severity-based alert routing (info, warning, critical)
- Predictive alerts (e.g., "soil moisture will reach critical in 24h")

### 📱 Interactive Dashboard
- Farm overview with key metrics
- Plot-level monitoring and comparison
- Irrigation and nutrient management views
- Financial dashboards
- Customizable date ranges and filters
- Export capabilities (CSV, PDF)

## Technology Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **PostgreSQL 14+** - Robust relational database
- **TimescaleDB** - Time-series data optimization
- **Redis** - Caching and task queue
- **Celery** - Asynchronous task processing

### Frontend
- **React 18+** with TypeScript
- **Material-UI / shadcn/ui** - Component library
- **Recharts** - Data visualization
- **React-Leaflet** - Farm/plot mapping

### Data Processing
- **pandas** - CSV/Excel parsing and manipulation
- **numpy** - Numerical computations
- **scikit-learn** - Machine learning and analytics

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **MinIO** - S3-compatible file storage

## Project Structure

```
FarmFactory/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # REST API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/         # API validation schemas
│   │   ├── services/        # Business logic
│   │   ├── tasks/           # Celery tasks
│   │   └── utils/           # Utilities
│   ├── alembic/             # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── hooks/           # Custom hooks
│   └── package.json
├── docker-compose.yml       # Container orchestration
├── templates/               # CSV import templates
└── docs/                    # Documentation

```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 4GB+ RAM recommended

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FarmFactory
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First Steps

1. **Create a farm**: Navigate to the dashboard and add your first farm
2. **Add plots**: Define your field/plot boundaries
3. **Download CSV templates**: Get standardized templates for data import
4. **Import data**: Upload your historical data (irrigation, nutrients, soil tests)
5. **Configure alerts**: Set threshold values for monitoring
6. **Explore dashboards**: View insights and recommendations

## Data Import

### Supported Data Types

1. **Farm & Plot Data**: Location, area, soil profiles
2. **Irrigation Events**: Date, method, duration, volume
3. **Nutrient Applications**: Date, type, amount, NPK ratios, costs
4. **Water Quality**: pH, EC, TDS, temperature, dissolved oxygen
5. **Environmental Data**: Temperature, humidity, soil moisture, rainfall
6. **Phenology Observations**: Growth stages, plant height, health scores
7. **Financial Data**: Input costs, harvest revenues

### CSV Template Format

Download templates from the dashboard or see `/templates` directory. Example:

```csv
date_time,plot_name,method,duration_minutes,water_volume_liters
2024-01-15 06:00,North Field,drip,120,500
2024-01-16 06:00,South Field,sprinkler,90,800
```

### Import Process

1. Upload CSV/Excel file
2. Preview data and map columns
3. Validate data
4. Process import (handles large files in batches)
5. Review import report

## Database Schema

The system uses a comprehensive relational schema with time-series optimization:

- **Core entities**: Farms, Plots, Crops, Plantings
- **Time-series data**: Irrigation, Nutrients, Water Quality, Environmental Readings
- **Supporting data**: Soil Profiles, Phenology Observations, Alerts
- **Financial data**: Input Costs, Harvests, Revenue

See `FARM_OPTIMIZATION_PLAN.md` for detailed schema documentation.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Calls

```bash
# List all farms
curl http://localhost:8000/api/v1/farms

# Get plot irrigation data
curl http://localhost:8000/api/v1/plots/{plot_id}/irrigation?start_date=2024-01-01&end_date=2024-12-31

# Get analytics
curl http://localhost:8000/api/v1/plots/{plot_id}/analytics/yield-trends
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://farm_user:password@localhost:5432/farmfactory

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIR=/app/uploads

# Alerts
ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

## Dashboard Features

### Overview Dashboard
- Farm summary statistics
- Active alerts
- Key performance indicators
- Quick access to recent activities

### Plot Monitoring
- Real-time sensor readings
- Soil moisture and temperature trends
- Irrigation schedule and history
- Growth stage tracking

### Irrigation Management
- Water usage analytics
- Efficiency metrics
- Cost tracking
- Automated scheduling recommendations

### Nutrient Management
- NPK balance tracking
- Application history
- Cost per kg of yield
- Optimization suggestions

### Financial Dashboard
- Profit & loss by plot/crop
- Input cost breakdown
- Revenue tracking
- ROI analysis

### Analytics
- Yield predictions
- Input efficiency analysis
- Comparative performance
- Optimization recommendations

## Alert Configuration

### Setting Up Alerts

1. Navigate to Settings > Alert Thresholds
2. Select plot and parameter (e.g., soil moisture)
3. Set min/max values
4. Choose severity level
5. Configure notification preferences

### Alert Types

- **Critical**: Requires immediate action (e.g., soil moisture critical)
- **Warning**: Attention needed (e.g., trending outside optimal range)
- **Info**: Informational (e.g., harvest window approaching)

## Performance

The system is designed for:
- **API response time**: <200ms (95th percentile)
- **Dashboard load time**: <2 seconds
- **File import speed**: 10,000+ rows/minute
- **Real-time updates**: <1 second latency
- **Database**: Handles millions of time-series records efficiently

## Security

- JWT-based authentication
- Role-based access control (Admin, Manager, Viewer)
- HTTPS encryption in transit
- Database encryption at rest
- Regular automated backups
- Audit logging

## Deployment

### Production Deployment

1. Use provided `docker-compose.prod.yml`
2. Configure environment variables for production
3. Set up SSL certificates (Let's Encrypt recommended)
4. Configure backup automation
5. Set up monitoring (Prometheus, Grafana)

### Cloud Deployment

Supports deployment on:
- AWS (ECS, RDS, S3)
- Google Cloud Platform (Cloud Run, Cloud SQL)
- Azure (Container Instances, PostgreSQL)
- DigitalOcean (App Platform, Managed Databases)

## Roadmap

### Current Version (v1.0)
- Core data import and management
- Real-time dashboards
- Alert system
- Basic analytics

### Planned Features (v2.0)
- Mobile applications (iOS/Android)
- Satellite imagery integration
- Computer vision for pest/disease detection
- Advanced ML yield prediction
- Automated irrigation control

### Future Enhancements
- Prescription mapping (variable rate application)
- Carbon footprint tracking
- Multi-farm management
- Agronomist collaboration features

## Support

- **Documentation**: See `/docs` directory
- **API Docs**: http://localhost:8000/docs
- **Issues**: Submit issues on GitHub
- **Email**: support@farmfactory.example.com

## Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License details to be added]

## Acknowledgments

Built with modern technologies and best practices for agricultural data management.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-16
**Status**: Development
