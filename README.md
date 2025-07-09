# Invoice Generator

A modern, full-stack invoice generation application built with FastAPI and React. Create, manage, and export professional invoices with ease.

## Features

- **Invoice Management**
  - Create and edit invoices with customizable details
  - Add multiple line items with descriptions, quantities, and prices
  - Automatic calculation of subtotals, taxes, and totals
  - Support for multiple currencies

- **Client & Vendor Information**
  - Store and manage client details
  - Customizable vendor information
  - Save default settings for quick invoice creation

- **PDF Export**
  - Generate professional PDF invoices
  - Customizable invoice templates
  - Download or preview invoices

- **Modern UI**
  - Responsive React-based interface
  - Real-time updates and calculations
  - Clean, intuitive design with Tailwind CSS

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **Alembic** - Database migration tool
- **ReportLab** - PDF generation
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Router** - Client-side routing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server for frontend
- **PostgreSQL** - Production database

## Prerequisites

### For Docker Installation (Recommended)
- Docker Engine 20.10+
- Docker Compose 2.0+

### For Manual Installation
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd invoice-gen
   ```

2. Copy the environment example file:
   ```bash
   cp .env.example .env
   ```

3. Update the `.env` file with your configuration (especially the SECRET_KEY for production)

4. Build and start the services:
   ```bash
   docker-compose up -d --build
   ```

5. The application will be available at:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install asyncpg psycopg2-binary  # For PostgreSQL support
   ```

4. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Ensure VITE_API_URL points to your backend
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. The frontend will be available at http://localhost:3000

## Usage

1. **Access the Application**
   - Open your browser and navigate to http://localhost (Docker) or http://localhost:3000 (manual)

2. **Create Your First Invoice**
   - Click "New Invoice" on the dashboard
   - Fill in vendor and client details
   - Add line items with descriptions and amounts
   - Set tax rates and payment terms
   - Preview and save the invoice

3. **Export to PDF**
   - Open any saved invoice
   - Click the "Download PDF" button
   - The PDF will be generated and downloaded

4. **Manage Defaults**
   - Set default vendor information
   - Configure default tax rates
   - Save preferred currency settings

## API Documentation

The backend provides a RESTful API with automatic documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/invoices` - List all invoices
- `POST /api/invoices` - Create a new invoice
- `GET /api/invoices/{id}` - Get invoice details
- `PUT /api/invoices/{id}` - Update an invoice
- `DELETE /api/invoices/{id}` - Delete an invoice
- `GET /api/invoices/{id}/pdf` - Generate PDF for an invoice
- `GET /api/defaults` - Get user defaults
- `PUT /api/defaults` - Update user defaults

## Project Structure

```
invoice-gen/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core configuration and database
│   │   ├── crud/         # Database operations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client services
│   │   └── types/        # TypeScript type definitions
│   └── Dockerfile
├── docker-compose.yml    # Docker orchestration
└── README.md
```

## Development

### Running Tests

#### Backend Tests
```bash
cd backend
pytest
```

#### Frontend Tests
```bash
cd frontend
npm test
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: ESLint and Prettier configurations are included

## Production Deployment

1. **Update Environment Variables**
   - Set `DEBUG=false` in production
   - Use a strong `SECRET_KEY`
   - Configure proper database credentials
   - Set appropriate CORS origins

2. **Security Considerations**
   - Use HTTPS in production
   - Configure proper CORS settings
   - Keep dependencies updated
   - Use environment variables for sensitive data

3. **Scaling**
   - The application is stateless and can be horizontally scaled
   - Use a load balancer for multiple backend instances
   - Configure PostgreSQL for production workloads

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify network connectivity between services

2. **CORS Errors**
   - Update CORS origins in `backend/app/main.py`
   - Ensure frontend API URL is correctly configured

3. **Build Failures**
   - Clear Docker cache: `docker-compose build --no-cache`
   - Check for port conflicts
   - Ensure all dependencies are properly installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.