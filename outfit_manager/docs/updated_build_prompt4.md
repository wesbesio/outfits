# 🎯 Outfit Manager - Complete Build Instructions

## 📋 Project Overview
Build a modern fashion outfit management system using FastAPI + HTMX with a beautiful purple-themed UI. Users can manage clothing components, create outfits, and organize their wardrobe with image uploads, filtering, and interactive scoring functionality.

## 🏗️ Architecture Requirements

### Backend Stack
- **Framework**: FastAPI with SQLModel for database ORM
- **Database**: SQLite with BLOB storage for images  
- **Image Processing**: Pillow for validation, compression, thumbnails
- **Templates**: Jinja2 for server-side rendering
- **API**: RESTful endpoints with HTMX-compatible HTML responses
- **Error Handling**: Robust parameter validation and user-friendly error messages

### Frontend Stack
- **Interactions**: HTMX for all dynamic behavior (NO vanilla JavaScript)
- **Styling**: Custom CSS with CSS variables and responsive design
- **UI Pattern**: Full-page forms preferred over modals
- **Mobile**: Mobile-first responsive design with touch-friendly interactions
- **Error Feedback**: Enhanced error handling with auto-hiding toasts and context-aware messages

## 📊 Database Schema

### Core Models
```python
# File: models/__init__.py
# Revision: 5.0 - Complete model definitions with score functionality

# Vendor: Shopping sources (Amazon, Poshmark, etc.)
class Vendor:
    venid: int (PK)
    name: str
    description: Optional[str] 
    active: bool = True
    flag: bool = False

# Piece: Clothing categories (Shirt, Pants, Shoes, etc.)
class Piece:
    piecid: int (PK)
    name: str
    description: Optional[str]
    active: bool = True

# Component: Individual clothing items
class Component:
    comid: int (PK)
    name: str
    brand: Optional[str]
    cost: int = 0
    description: Optional[str]
    notes: Optional[str]
    vendorid: Optional[int] (FK)
    pieceid: Optional[int] (FK)
    image: Optional[bytes] = None  # BLOB storage
    active: bool = True
    flag: bool = False

# Outfit: Collections of components with scoring system
class Outfit:
    outid: int (PK)
    name: str
    description: Optional[str]
    notes: Optional[str]
    totalcost: int = 0
    score: int = 0  # Interactive scoring system (0+)
    image: Optional[bytes] = None  # BLOB storage
    active: bool = True
    flag: bool = False

# Out2Comp: Many-to-many relationship
class Out2Comp:
    o2cid: int (PK)
    outid: int (FK)
    comid: int (FK)
    active: bool = True
    flag: bool = False
```

## 🎨 Design System

### Color Palette
```css
/* File: static/css/main.css */
/* Revision: 5.0 - Complete design system with score styling */

:root {
    --primary-color: #8B5CF6;      /* Main purple */
    --primary-dark: #7C3AED;       /* Darker purple */
    --primary-light: #A78BFA;      /* Lighter purple */
    --secondary-color: #EC4899;    /* Pink accent */
    --accent-color: #F3E8FF;       /* Light purple */
    
    --bg-gradient: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 50%, #F0F4FF 100%);
    --card-bg: rgba(255, 255, 255, 0.9);
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
}
```

### UI Principles
- **Glassmorphism effects** with backdrop-filter
- **Card-based layouts** with hover animations
- **Purple gradient backgrounds** throughout
- **Touch-friendly** 44px minimum touch targets
- **Smooth transitions** for all interactions
- **Interactive score controls** with visual feedback and centered alignment
- **Context-aware error messages** with auto-hiding toasts

## 🚀 Core Features to Implement

### 1. Component Management
```python
# File: routers/components.py  
# Revision: 1.5 - Complete component CRUD with enhanced search error handling

# Routes needed:
# GET /api/components/ - List with filters (HTML/JSON) - FIXED: Proper parameter handling
# POST /api/components/ - Create with multipart image upload
# GET /components/{id} - Detail view with outfits section
# PUT /api/components/{id} - Update
# DELETE /api/components/{id} - Soft delete
# POST /api/components/{id}/upload-image - Image upload
# GET /api/components/{id}/outfits - HTML list of outfits using component
```

### 2. Outfit Management with Scoring
```python
# File: routers/outfits.py
# Revision: 1.21 - Complete outfit CRUD with clean score interface and search fixes

# Routes needed:
# GET /api/outfits/ - List with calculated costs and scores (HTML/JSON) - FIXED: Error handling
# POST /api/outfits/ - Create with multipart image upload and score
# GET /outfits/{id} - Detail view with components and centered score controls
# PUT /api/outfits/{id} - Update with score field
# POST /api/outfits/{id}/score/increment - HTMX increment score (+1)
# POST /api/outfits/{id}/score/decrement - HTMX decrement score (-1, min 0)
# POST /api/outfits/{id}/components/{component_id} - Add component
# DELETE /api/outfits/{id}/components/{component_id} - Remove component
# GET /api/outfits/{id}/components - HTML list of components in outfit
```

### 3. Interactive Score System
```python
# File: routers/outfits.py
# Revision: 1.21 - Clean score management endpoints

@router.post("/api/outfits/{outid}/score/increment")
async def increment_outfit_score():
    # Increment score by 1
    # Return HTML fragment with centered score display (no label)
    # Include functional +/- buttons

@router.post("/api/outfits/{outid}/score/decrement") 
async def decrement_outfit_score():
    # Decrement score by 1 (minimum 0)
    # Return HTML fragment with centered score display (no label)
    # Disable minus button when score = 0
```

### 4. Enhanced Search and Filter System
```python
# File: routers/components.py & routers/outfits.py
# Revision: 1.5+ - Robust search parameter handling

# CRITICAL: Safe parameter conversion for search filters
def safe_int_conversion(value: Optional[str]) -> Optional[int]:
    """Safely convert string to int, returning None for empty/invalid values."""
    if not value or not value.strip():
        return None
    try:
        return int(value)
    except ValueError:
        return None

# Search endpoints MUST use Optional[str] for filter parameters, not Optional[int]
@router.get("/api/components/")
async def list_components_api(
    vendorid: Optional[str] = None,  # REQUIRED: Use str, not int
    pieceid: Optional[str] = None,   # REQUIRED: Use str, not int
    # Then convert safely using safe_int_conversion()
):
```

### 5. Image Upload System
```python
# File: services/image_service.py
# Revision: 3.0 - Robust image processing

class ImageService:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_IMAGE_SIZE = (1200, 1200)
    THUMBNAIL_SIZE = (300, 300)
    
    @classmethod
    async def validate_and_process_image(cls, file: UploadFile) -> bytes:
        # Validate size and format
        # Resize if needed
        # Convert to JPEG
        # Return compressed bytes
```

### 6. Enhanced Error Handling System
```javascript
// File: static/js/form-error-handler.js
// Revision: 1.1 - Enhanced error handling with validation error detection

// CRITICAL: Must handle FastAPI validation errors (422) properly
// Must provide context-aware error messages
// Must implement auto-hiding for non-critical errors
// Must include request throttling for search operations
```

### 7. Form Implementation
- **Full-page forms** instead of modals
- **HTMX form submission** with proper redirects
- **Image upload** with drag & drop + file selection
- **Score input fields** for manual score editing
- **Real-time validation** feedback with enhanced error messages
- **Error handling** with user-friendly messages and context

## 🚨 CRITICAL: Auto-Loading Prevention Guidelines

**The #1 cause of form loading failures is auto-loading HTMX elements.**

### Auto-Loading Rule
```html
<!-- ❌ NEVER in multi-purpose templates -->
<div hx-trigger="load">

<!-- ✅ ALWAYS use conditional or manual loading -->
<button hx-get="/api/data" hx-target="#container">Load Data</button>
```

### Route Order Rule  
```python
# ✅ Specific routes FIRST
@router.get("/entities/new")
@router.get("/entities/{id}")  
@router.get("/entities/")

# ❌ General routes first breaks routing
@router.get("/entities/")      # Catches everything!
@router.get("/entities/new")   # Never reached
```

## 🔧 Key Implementation Details

### CRITICAL: Search Parameter Handling
```python
# ❌ WRONG - Causes "[object Object]" errors
@router.get("/api/components/")
async def list_components_api(
    vendorid: Optional[int] = None,  # Fails with empty string ""
    pieceid: Optional[int] = None,   # Fails with empty string ""
):

# ✅ CORRECT - Handles HTML form data properly
@router.get("/api/components/")
async def list_components_api(
    vendorid: Optional[str] = None,  # Accepts empty strings
    pieceid: Optional[str] = None,   # Accepts empty strings
):
    # Convert safely
    vendorid_int = safe_int_conversion(vendorid)
    pieceid_int = safe_int_conversion(pieceid)
```

### Enhanced Error Handling Pattern
```python
# REQUIRED: All search/list endpoints must use this pattern
try:
    # Database query operations
    query = select(Model).where(Model.active == True)
    # Apply filters, sorting, etc.
    results = session.exec(query).all()
    return templates.TemplateResponse("template.html", context)
except Exception as e:
    print(f"Error in endpoint: {e}")  # Log for debugging
    # Return user-friendly error HTML instead of exception
    error_html = f"""
    <div class="error-container">
        <p>Sorry, there was an error loading data.</p>
        <p>Please try refreshing the page.</p>
    </div>
    """
    return HTMLResponse(content=error_html, status_code=200)
```

### HTMX Patterns
```html
<!-- Content negotiation based on Accept header -->
<div hx-get="/api/components/" 
     hx-headers='{"Accept": "text/html"}'
     hx-target="#components-grid"
     hx-trigger="load">

<!-- Form submission with redirect -->
<form hx-post="/api/components/"
      hx-encoding="multipart/form-data"
      hx-target="#main-content"
      hx-swap="outerHTML">

<!-- Score increment/decrement buttons (no label) -->
<button hx-post="/api/outfits/{id}/score/increment"
        hx-target="#outfit-score-display"
        hx-swap="outerHTML">+</button>

<!-- Dynamic loading with indicators -->
<select hx-get="/api/vendors"
        hx-trigger="load"
        hx-target="this"
        hx-swap="innerHTML">
```

### Score System Implementation
```css
/* File: static/css/main.css */
/* Revision: 5.1 - Centered score control styling with proper spacing */

.score-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-sm);
}

.score-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    background-color: var(--accent-color);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-md);
}

.btn-score-plus, .btn-score-minus {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
}

.score-badge {
    /* Color-coded score indicators */
    /* Gray (0-2), Pink (3-4), Purple (5+) */
}
```

### Enhanced No Results Templates
```html
<!-- File: templates/components/list_content.html -->
<!-- Revision: 1.1 - Context-aware no results messaging -->

{% if components %}
    <!-- Show components -->
{% else %}
    <div class="no-results-container">
        <div>🔍 No components found</div>
        <p>
            {% if request.query_params.get('q') %}
                No components match your search for "<strong>{{ request.query_params.get('q') }}</strong>".
            {% elif request.query_params.get('vendorid') or request.query_params.get('pieceid') %}
                No components match your selected filters.
            {% else %}
                You haven't added any components yet.
            {% endif %}
        </p>
        <!-- Clear search and add new buttons -->
    </div>
{% endif %}
```

### Image Upload Implementation
```html
<!-- File: templates/forms/component_form.html -->
<!-- Revision: 4.0 - Simplified upload approach -->

<div class="upload-container">
    <input type="file" name="file" accept="image/*" style="display: none;">
    <button type="button" class="upload-button">Select Image</button>
    <div class="preview-area"></div>
</div>

<script>
// Minimal JavaScript for preview only
// Main upload handled by HTMX form submission
</script>
```

### Responsive Design
```css
/* File: static/css/main.css */
/* Revision: 5.1 - Mobile-first responsive with centered score controls */

/* Mobile-first approach */
.card-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
}

/* Score controls responsive behavior */
@media (max-width: 767px) {
    .btn-score-plus, .btn-score-minus {
        min-width: 44px; /* Touch-friendly */
        min-height: 44px;
    }
}

/* Tablet and up */
@media (min-width: 768px) {
    .card-grid {
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    }
}
```

## 📁 File Structure Requirements

```
outfit_manager/
├── main.py                          # FastAPI app with web routes
├── requirements.txt                 # Python dependencies
├── debug.py                         # Project validation script
├── add_score_field.py              # Database migration script for score
├── models/
│   ├── __init__.py                 # All SQLModel definitions with score
│   └── database.py                 # Database configuration
├── routers/
│   ├── __init__.py
│   ├── outfits.py                  # Outfit CRUD + Score endpoints + HTML responses (Rev 1.21+)
│   ├── components.py               # Component CRUD + HTML responses (Rev 1.5+)
│   ├── vendors.py                  # Vendor management
│   ├── pieces.py                   # Piece type management
│   └── images.py                   # Image serving endpoints
├── services/
│   ├── __init__.py
│   ├── image_service.py            # Image processing utilities
│   └── seed_data.py               # Initial data creation
├── templates/
│   ├── base.html                   # Base template with HTMX
│   ├── components/
│   │   ├── list.html              # Full page
│   │   ├── list_content.html      # HTMX content-only (Rev 1.1+)
│   │   ├── detail.html            # Full page  
│   │   └── detail_content.html    # HTMX content-only
│   ├── outfits/
│   │   ├── list.html              # Full page
│   │   ├── list_content.html      # HTMX content-only with score badges (Rev 1.1+)
│   │   ├── detail.html            # Full page
│   │   └── detail_content.html    # HTMX content-only with centered score controls
│   ├── forms/
│   │   ├── component_form.html         # Full page
│   │   ├── component_form_content.html # HTMX content-only
│   │   ├── outfit_form.html            # Full page
│   │   ├── outfit_form_content.html    # HTMX content-only with score field
│   │   ├── vendor_form.html            # Full page
│   │   └── vendor_form_content.html    # HTMX content-only
│   └── partials/
│       ├── component_cards.html    # Card grid for components
│       ├── outfit_cards.html       # Card grid for outfits with score badges
│       ├── vendor_options.html     # Select options
│       └── piece_options.html      # Select options
└── static/
    ├── css/
    │   └── main.css               # Complete styling system with score styles
    └── js/
        ├── main.js                # Minimal utilities only
        ├── form-error-handler.js  # HTMX error handling (Rev 1.1+)
        └── image-preview.js       # Image upload preview
```

## ✅ Debug Script Requirements

```python
# File: debug.py
# Revision: 6.0 - Complete project validation with search error testing

required_structure = [
    # All directories and files from structure above
    # Update to check for:
    # - Content-only templates for HTMX
    # - Image upload functionality  
    # - Score management endpoints
    # - Proper routing structure
    # - Enhanced error handling
    # - Search parameter validation
    # - CSS and JS files
]

def check_template_structure():
    # Verify all templates exist
    # Check for both full and content-only versions
    # Validate HTMX attributes and patterns
    
def check_api_endpoints():
    # Verify all required routes are defined
    # Check for proper HTML/JSON content negotiation
    # Validate multipart form handling
    # Verify score increment/decrement endpoints
    # TEST: Search parameter handling with empty strings
    
def check_search_error_handling():
    # TEST: Search with empty vendorid/pieceid parameters
    # TEST: Search with invalid parameters
    # TEST: Search with no results found
    # Verify proper error messages returned
    
def check_image_upload():
    # Verify image service implementation
    # Check upload endpoints exist
    # Validate file handling and storage

def check_htmx_auto_loading():
    # Verify no problematic auto-loading patterns
    # Check template files for hx-trigger="load" usage
    # Validate route order in routers
    
def test_form_loading():
    # Test each "Add New" form loads cleanly
    # Verify no immediate secondary requests
    # Check browser network tab behavior

def test_score_functionality():
    # Test score increment/decrement endpoints
    # Verify score validation (minimum 0)
    # Check HTMX score control behavior
    # Verify centered alignment and proper spacing

def test_search_functionality():
    # NEW: Test search with various parameter combinations
    # TEST: Empty strings for vendorid/pieceid
    # TEST: Invalid integer values
    # TEST: No results found scenarios
    # Verify user-friendly error messages
```

## 🎯 Implementation Priority

### Phase 1: Core Foundation ✅
1. ✅ Database models and relationships
2. ✅ Basic FastAPI setup with static files
3. ✅ Base template with HTMX integration
4. ✅ CSS design system implementation

### Phase 2: Component Management ✅ 
1. ✅ Component CRUD endpoints
2. ✅ Component list and detail templates
3. ✅ Component form with image upload
4. ✅ Image service and processing
5. ✅ Enhanced search parameter handling
6. ✅ Error handling and user-friendly messages
7. **🧪 TESTING: Verify "Add New" loads without extra requests**

### Phase 3: Outfit Management with Scoring ✅
1. ✅ Outfit CRUD endpoints with score field
2. ✅ Outfit list and detail templates with score display
3. ✅ Outfit form with image upload and score input
4. ✅ Component-outfit relationship management
5. ✅ Interactive score increment/decrement functionality
6. ✅ Score validation and UI feedback
7. ✅ Clean, centered score interface without redundant labels
8. ✅ Enhanced search error handling
9. **🧪 TESTING: Verify form loading, route order, score controls, and search reliability**

### Phase 4: Advanced Features ✅
1. ✅ Filtering and sorting (including by score)
2. ✅ Responsive mobile optimization
3. ✅ Error handling and validation with enhanced UX
4. ✅ Database migration for score field
5. ✅ Context-aware "no results" messaging
6. ✅ Auto-hiding error toasts
7. ✅ Request throttling for search operations

### Phase 5: Polish and Testing ✅
1. ✅ Search parameter validation testing
2. ✅ Error message UX testing
3. ✅ Mobile responsiveness verification
4. ✅ Score functionality end-to-end testing
5. ✅ Search reliability across all scenarios

## 🚫 What NOT to Include

- **No modals** - Use full-page forms instead
- **Minimal JavaScript** - Let HTMX handle interactions
- **No client-side routing** - Server-side navigation with HTMX
- **No complex state management** - Server renders all state
- **No localStorage** - Not supported in Claude artifacts

## 📝 File Header Convention

Every code file must start with:
```html
<!-- File: path/to/file.html -->
<!-- Revision: X.X - Description of changes/purpose -->
```

Every Python file must start with:
```python
# File: path/to/file.py
# Revision: X.X - Description of changes/purpose
```

## Guidelines for utilities or debug scripts
- **Should be located in the utilities folder**
- **Should follow the file naming conventions**

## 🎉 Success Criteria

- ✅ Beautiful purple-themed responsive UI
- ✅ Full CRUD operations for components and outfits  
- ✅ Working image upload with thumbnails
- ✅ Interactive outfit scoring system with clean, centered +/− buttons
- ✅ Score validation and visual feedback
- ✅ Color-coded score badges in list views
- ✅ Database migration support for score field
- ✅ Smooth HTMX interactions without page refreshes
- ✅ Mobile-friendly touch interface with accessible score controls
- ✅ **Enhanced search reliability with proper parameter handling**
- ✅ **User-friendly error messages instead of "[object Object]"**
- ✅ **Context-aware "no results found" messaging**
- ✅ **Auto-hiding error toasts with manual dismiss for critical errors**
- ✅ **Request throttling to prevent rapid-fire search issues**
- ✅ Proper error handling and validation
- ✅ Organized, maintainable codebase

## 🎯 Score System Features

### Interactive Controls
- **Plus Button**: Increment score by 1 (unlimited)
- **Minus Button**: Decrement score by 1 (minimum 0, button disabled at 0)
- **Visual Feedback**: Smooth animations and color transitions
- **HTMX Integration**: Real-time updates without page refresh
- **Clean Interface**: No redundant labels, centered alignment with proper spacing

### Score Display
- **Detail View**: Interactive +/− buttons with current score (centered, no label)
- **List View**: Color-coded score badges (gray/pink/purple for low/medium/high)
- **Form View**: Manual score input field with validation and helpful label

### Database Integration
- **Migration Script**: Safe addition of score field to existing data
- **Validation**: Server-side validation ensures score ≥ 0
- **Persistence**: Score saved with outfit data

## 🔍 Search System Features

### Enhanced Parameter Handling
- **Safe Conversion**: Empty strings converted to None properly
- **Type Safety**: Optional[str] parameters with safe_int_conversion()
- **Validation**: Fallback to defaults for invalid sort parameters
- **Error Recovery**: Graceful handling of malformed requests

### User Experience
- **Context-Aware Messages**: "No components match your search for 'xyz'"
- **Clear Search Buttons**: Easy recovery from filtered states
- **Auto-Hide Toasts**: Non-critical errors dismiss automatically
- **Request Throttling**: Prevents rapid-fire search issues

### Error Handling
- **FastAPI Validation Errors (422)**: "Please check your input values"
- **Search Parameter Errors (400)**: "Invalid search parameters"
- **Network Errors**: "Connection issue, please check your internet"
- **Server Errors (500+)**: "Server error, please try again"

## 🚨 Critical Search Requirements

### MANDATORY Parameter Patterns
```python
# ✅ REQUIRED for all search/filter endpoints
@router.get("/api/items/")
async def search_items(
    filter_param: Optional[str] = None,  # Must be str, not int
):
    converted_param = safe_int_conversion(filter_param)
    # Use converted_param in queries
```

### MANDATORY Error Handling
```python
# ✅ REQUIRED for all API endpoints
try:
    # Database operations
    return templates.TemplateResponse("template.html", context)
except Exception as e:
    print(f"Error: {e}")  # Log for debugging
    return HTMLResponse(content=friendly_error_html, status_code=200)
```

### MANDATORY No Results Templates
```html
<!-- ✅ REQUIRED context-aware messaging -->
{% if items %}
    <!-- Show items -->
{% else %}
    <div class="no-results">
        {% if request.query_params.get('q') %}
            No items match your search for "<strong>{{ request.query_params.get('q') }}</strong>".
        {% else %}
            No items found.
        {% endif %}
        <!-- Clear search button if filters applied -->
    </div>
{% endif %}
```

## Documentation to review

https://htmx.org/quirks/

## 🎯 Recent Fixes Implemented

### Search Error Resolution (Latest Update)
- ✅ **Fixed "[object Object]" Error**: Proper parameter type handling in search endpoints
- ✅ **Enhanced Error Messages**: Context-aware, user-friendly error feedback
- ✅ **Improved No Results UX**: Shows search terms and provides clear actions
- ✅ **Request Throttling**: Prevents rapid search requests that could cause issues
- ✅ **Auto-Hide Error Toasts**: Better UX with automatic dismissal for non-critical errors

These fixes ensure robust search functionality that gracefully handles all edge cases while providing excellent user experience.