# Wallet Watcher

A comprehensive personal finance management application built with Django that helps you track your expenses, manage budgets, visualize spending patterns, and generate financial reports.

## Overview

Wallet Watcher is a robust financial management system designed to give users complete control over their personal finances. With intuitive interfaces for tracking transactions, setting budgets, and generating insightful reports, it helps users make informed financial decisions and develop better spending habits.

## Tech Stack

- **Backend Framework**: Django 5.0.2
- **Database**: Configurable (Default: SQLite, supports MySQL/PostgreSQL)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Authentication**: Django Allauth
- **Form Processing**: Django Crispy Forms with Tailwind
- **PDF Generation**: ReportLab
- **Email**: SMTP (configurable for production)

## Features

### User Management

- Custom user model with extended profile information
- Email-based authentication
- Profile management with theme preferences
- Secure password reset functionality

### Dashboard

- Customizable time period views (daily, weekly, monthly, yearly)
- Overview of income, expenses, and net balance
- Budget status tracking and visualization
- Recent transactions list
- Top spending categories
- Balance history charts

### Transactions

- Track both income and expenses
- Categorize transactions
- Link transactions to budgets
- Advanced filtering and searching
- Import/export transaction data

### Budgets

- Create budgets with different time periods (daily, weekly, monthly, yearly)
- Track spending against budgets
- Visual indicators for budget status
- Automatic tracking of remaining amounts

### Reports

- Generate detailed financial reports
- Customizable date ranges and filtering options
- Export as PDF
- Visual charts and graphs for better data visualization
- Category breakdown of income and expenses
- Balance history tracking

## Application Structure

- **accounts**: User authentication and profile management
- **dashboard**: Main dashboard views and visualization
- **transactions**: Transaction management and categorization
- **budgets**: Budget creation and tracking
- **reports**: Financial report generation
- **seeders**: Data seeding scripts for development and testing

## Installation and Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- virtualenv (recommended)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd wallet_watcher
   ```

2. **Create and activate a virtual environment**

   ```bash
   # On Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:

   ```plaintext
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (Optional - defaults to SQLite)
   DB_ENGINE=sqlite3
   DB_NAME=budget_tracker
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=
   
   # Email (Optional for development)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-email-password
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Seed sample data (optional)**

   ```bash
   python seeders/run_all_seeders.py
   ```

8. **Run the development server**

   ```bash
   python manage.py runserver
   ```

9. **Visit the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## Development

### Creating New Apps

```bash
python manage.py startapp new_app_name
```

## Deployment

For production deployment, consider the following:

1. Set `DEBUG=False` in your .env file
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper SMTP email service
4. Use a production web server like Gunicorn
5. Configure Nginx or Apache as a reverse proxy
6. Set up static file serving with whitenoise or a cloud storage service

## License

MIT License

## Acknowledgements

- Django project and its contributors
- All the open-source libraries used in this project
