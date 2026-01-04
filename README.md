# Style Forecast
Style Forecast is a web-based platform developed as a group project for Module University Vienna.  
The project was created as part of a university coursework assignment and demonstrates the practical
application of web development concepts, including frontend–backend integration and database-driven design.

The application helps users manage a digital wardrobe, track clothing usage, save outfit history,
and maintain personal profile preferences.

## Tech Stack
- Backend: Python, Flask (Blueprint-based architecture)
- Database: MongoDB
- Frontend: HTML, Bootstrap, JavaScript
- Authentication: JWT

## Pages and Features

### Index (Landing Page)
- Project introduction and feature overview
- Navigation to authentication page

### Wardrobe
- Add, view, update, and delete clothing items
- Filter items by category or status
- Toggle item status (Clean ↔ Needs Wash)
- Automatic wear count tracking

### Outfit History
- Store generated outfits
- Display saved outfits as cards
- Delete outfit history entries

### Profile
- View and update user profile information
- Change password (bcrypt hashing)
- Manage personal preferences (gender, age, days until dirty)

### Authentication (Login / Signup)
- User registration and login
- Secure password handling with bcrypt hashing
- Access control to protected application pages

### Accessories
- View and manage accessory items
- Store accessory data for outfit enhancement
- Integration with outfit-related functionality

### Get Outfit
- Generate outfit suggestions based on wardrobe items
- Consider user-selected parameters (e.g. occasion, weather, location)
- Save generated outfits to Outfit History

### Plan Ahead
- Plan outfits for future dates
- Retrieve weather data for selected dates
- Create, update, rate, and delete planned outfits

## Project Structure

project/
├── app.py
├── model/
├── routes/
├── templates/
├── static/
└── utils/

### Folder Responsibilities

- **model/**  
  Contains all MongoDB-related logic (queries, inserts, updates, deletes).  
  No Flask routing or request handling is implemented here.

- **routes/**  
  Contains Flask Blueprints and route handlers.  
  Routes process HTTP requests, call model functions, and return HTML or JSON responses.

- **templates/**  
  Server-rendered HTML pages using Jinja2 templates.

- **static/**  
  Frontend assets:
  - CSS for styling
  - JavaScript for DOM manipulation and fetch-based API requests

- **utils/**  
  Shared utilities such as database connection and authentication helpers.

## Team Members and Roles

- Simran
  - Accessories module
  - Get Outfit module
  - Plan Ahead module
  - Authentication (Login / Signup)

- Sergei
  - Index (Landing Page)
  - Wardrobe module
  - Outfit History module
  - Profile module

  ## Setup Instructions
  ```bash
  pip install -r requirements.txt
  
  Run the application:
  python app.py
  
  Open the application in browser:
  http://127.0.0.1:5000/
