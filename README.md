# Style Forecast
Style Forecast is a web-based platform developed as a group project for Modul University Vienna.  
The project was created as part of a university coursework assignment and demonstrates the practical
application of web development concepts, including frontend–backend integration and database-driven design.

The application helps users manage a digital wardrobe, generate AI-powered outfit suggestions, track outfit history,
plan outfits for upcoming trips, and maintain personal style preferences.

## Tech Stack
- Backend: Python, Flask (Blueprint-based architecture)
- Database: MongoDB
- Frontend: HTML, Bootstrap 5.3.3, JavaScript (Vanilla)
- Authentication: JWT (secure token-based auth)
- AI/LLM: Groq API (outfit generation with Claude AI)
- Weather: OpenWeather API (weather data integration)
- Geolocation: Geocoding API (location-based services)

## Pages and Features

### Index (Landing Page)
- Project introduction and feature overview
- Quick navigation to authentication
- Responsive design showcasing key features

### Wardrobe
- **Add items** with color, category, type, and status
- **View all items** with real-time filtering by category and status
- **Edit items** - update name, color, category, type, or status
- **Delete items** with confirmation dialog
- **User-isolated** - each user only sees their own wardrobe
- **55+ sample items** pre-loaded for testing (casual, formal, gym outfits)
- Status tracking: Clean ↔ Needs Wash

### Accessories
- **Add, view, edit, delete** accessory items (necklaces, earrings, rings, bracelets, watches, bags, scarves, sunglasses, hats, belts)
- **User-isolated** - accessories only visible to owning user
- **25+ sample items** pre-loaded by category
- Integration with outfit generation for complete looks

### Get Outfit
- **AI-Powered Generation** using Groq API (Claude model)
- **Auto-weather detection** via OpenWeather API with temperature display
- **Occasion-based** outfit suggestions (Casual, Formal, Party, Gym, Rainy)
- **Location-aware** generation using coordinates
- **Like/Dislike** functionality for variety control
- **Save to History** with one click
- **Rate limiting** respected (11+ seconds between requests)

### Plan Ahead
- **Calendar view** with month/year navigation
- **Single-day planning** - generate outfit for any future date
- **Multi-day trips** - select date range and generate outfit for each day
- **Interactive slider** for navigating multi-day plans
- **Weather integration** - auto-detect or manually override weather
- **Save plans** to calendar for future reference
- **Location-based** outfit planning with autocomplete
- **Responsive design** with fixed dropdown sizing and smooth transitions
- User data isolated by email

### Outfit History
- **View all saved outfits** with date, location, occasion, weather
- **Delete entries** with confirmation
- **User-isolated** - only see own history
- **Persistence** across sessions

### Profile
- **View profile** with logged-in user email
- **Statistics display** (total outfits, saved plans, etc.)
- **User preferences** management
- **Secure access** - profile data only for authenticated user

### Authentication (Login / Signup)
- **Secure registration** with email and password
- **Login** with JWT token generation
- **Password hashing** with bcrypt
- **Session management** with token validation
- **Protected routes** - @token_required decorator on all private pages
- **User isolation** - all data filtered by current_user email

## Project Structure

```
project/
├── app.py                 # Flask app entry point
├── model/                 # Data layer (MongoDB logic)
│   ├── wardrobe_model.py
│   ├── accessories_model.py
│   ├── outfit_history_model.py
│   ├── plan_ahead_model.py
│   ├── get_outfit_model.py
│   └── login_model.py
├── routes/                # Route handlers (Flask Blueprints)
│   ├── wardrobe_routes.py
│   ├── accessories_routes.py
│   ├── history_routes.py
│   ├── plan_ahead_routes.py
│   ├── get_outfit_routes.py
│   ├── auth_routes.py
│   ├── profile_routes.py
│   └── intro_routes.py
├── templates/             # Jinja2 HTML templates
├── static/                # Frontend assets
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
└── utils/                 # Shared utilities
    ├── db.py              # MongoDB connection
    └── auth.py            # JWT authentication helpers
```

### Folder Responsibilities

- **model/**  
  Contains all MongoDB-related logic (queries, inserts, updates, deletes).  
  All functions accept `user_email` parameter for complete data isolation.  
  No Flask routing or request handling is implemented here.

- **routes/**  
  Contains Flask Blueprints and route handlers.  
  Routes process HTTP requests, validate user identity with JWT, call model functions with `current_user`, and return HTML or JSON responses.  
  All protected routes decorated with `@token_required`.

- **templates/**  
  Server-rendered HTML pages using Jinja2 templates.  
  Bootstrap 5.3.3 for responsive styling.

- **static/**  
  Frontend assets:
  - CSS files for styling each page
  - Vanilla JavaScript for DOM manipulation and fetch-based API requests
  - Event handlers for all buttons and forms

- **utils/**  
  Shared utilities:
  - Database connection and configuration
  - JWT authentication helpers and token validation
  - User extraction from token

## Data Isolation & Security

- **User Email Filtering**: All database queries filter by `user_email` parameter
- **JWT Authentication**: Tokens extracted and validated on protected routes
- **Bcrypt Hashing**: Passwords hashed before storage
- **No Data Leakage**: Users can only access their own wardrobe, accessories, history, and plans
- **Function Signatures**: All model functions updated to include `user_email` parameter

## Sample Data

Pre-loaded for `jane@example.com`:
- **33 Wardrobe Items**: 11 casual, 11 formal, 11 gym (3 complete outfits per category)
- **25 Accessories**: Across 10 categories (necklaces, earrings, rings, bracelets, watches, bags, scarves, sunglasses, hats, belts)

## Setup Instructions

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with:
# MONGO_URI=your_mongodb_connection_string
# GROQ_API_KEY=your_groq_api_key
# OPENWEATHER_API_KEY=your_openweather_api_key

# Run the application
python app.py

# Open in browser
http://127.0.0.1:5000/
```

## Team Members and Roles

- **Simran**
  - Accessories module
  - Get Outfit module (AI integration, weather API)
  - Plan Ahead module (calendar, slider, multi-day planning)
  - Authentication (Login / Signup)
  - User data isolation implementation

- **Sergei**
  - Index (Landing Page)
  - Wardrobe module
  - Outfit History module
  - Profile module

## Recent Updates

- ✅ Complete user data isolation across all features
- ✅ Fixed Plan Ahead slider navigation (prev/next directions)
- ✅ Fixed dropdown closure on slide navigation
- ✅ Fixed content bleeding between slider slides
- ✅ Added 58+ sample items for comprehensive testing
- ✅ Fixed wardrobe edit modal status field display
- ✅ Updated all function signatures to include user_email parameter
- ✅ Enhanced UI/UX with fixed dropdown sizing
- ✅ Comprehensive error handling and edge cases

## Testing Status

✅ All features tested and working  
✅ No crashes or errors  
✅ User isolation verified  
✅ Data persistence confirmed  
✅ UI/UX polished and responsive  
✅ Production-ready

## Error Handling & Robustness

The application gracefully handles the following error scenarios:

### Authentication & Authorization
- ✅ Invalid login credentials → Clear error message
- ✅ Session expired → Automatic redirect to login
- ✅ Duplicate email registration → Prevents signup with feedback
- ✅ Unauthorized access to other users' data → Blocked at database level

### Data Operations
- ✅ Missing required fields (name, color, type) → Validation error returned
- ✅ Database connection fails → Error message displayed to user
- ✅ Item not found for edit/delete → 404 error with message
- ✅ Invalid accessory ID → Validation error with try-catch handling
- ✅ Whitespace trimming on all inputs → Prevents invalid data entries

### API Integration
- ✅ Weather API unavailable → User can manually enter location/weather
- ✅ OpenWeather API fails → Outfit generation continues without weather context
- ✅ Groq API rate limit → User-friendly error message
- ✅ Invalid coordinates → Error handling with fallback options

### Data Integrity
- ✅ User email validation on every database operation → Prevents cross-user data leakage
- ✅ Try-catch blocks on all main routes → Graceful error recovery
- ✅ Null/undefined field checks → Prevents crashes from missing data
- ✅ All API endpoints return proper HTTP status codes → 200, 201, 400, 404, 500

## Innovation & Technical Highlights

Beyond basic requirements, this project includes:

### 1. AI-Powered Outfit Generation ⭐
- **Groq API Integration** with Claude LLM model
- **Natural language processing** for intelligent outfit suggestions
- **Context-aware recommendations** based on weather, occasion, and user preferences
- **Smart generation** - considers item condition, wear history, and seasonal appropriateness
- Provides detailed outfit explanations with reasoning

### 2. Real-Time Weather Integration ⭐
- **OpenWeather API** for live weather data and temperature
- **Temperature-based outfit suggestions** (prevents winter coats in summer!)
- **Location autocomplete** with coordinates and place names
- **Dynamic weather display** that updates automatically when location changes
- Enables weather-aware clothing recommendations

### 3. Intelligent Wear Tracking System ⭐
- **Automatic wear count increment** when outfit is saved to history
- **Wear diversity encouragement** - tracks how many times each item worn
- **Smart recommendations** can prioritize less-worn pieces
- **Prevents over-wearing** favorite items by tracking usage
- Helps identify underused wardrobe pieces

### 4. Advanced Multi-Day Trip Planning ⭐
- **Interactive calendar interface** for selecting date ranges
- **Multi-day outfit generation** - automatically generates outfit for each day of trip
- **Smooth slider UI** for navigating through trip days (previous/next)
- **Persistent plan storage** for future reference and modification
- Location-based planning with weather integration

### 5. Automatic Laundry Management ⭐
- **Smart status tracking** - items auto-marked "Needs Wash" after N days
- **Configurable threshold** per user (default: 3 days, customizable)
- **Prevents wearing unwashed clothes** - filtered from recommendations
- **Maintains wardrobe hygiene** automatically without user intervention
- Separate dirty_items collection for efficient laundry tracking

### 6. Secure Multi-User Architecture ⭐
- **Email-based user isolation** at database query level - all data filtered by user email
- **JWT authentication** with 24-hour token expiration for security
- **Bcrypt password hashing** - passwords never stored in plain text
- **No cross-user data leakage possible** - enforced at database level
- **Atomic database operations** using MongoDB `$inc` operator for wear_count
- **@token_required decorator** on all protected routes

### 7. Responsive & Polished UI/UX ⭐
- **Bootstrap 5.3.3** with 20+ custom components (modals, cards, forms, etc.)
- **Mobile-first design** works seamlessly on all screen sizes
- **Smooth animations** (fadeInUp, floatCloud, outfitUpdatedFlash) for better UX
- **Consistent design language** across all 8 pages and features
- **Interactive modals** for seamless CRUD operations without page reloads
- **Color-coded status indicators** for wardrobe item conditions
- **Icon-based categorization** for quick visual recognition
