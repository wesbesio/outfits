# Architecture Diagram Creation Prompt

## Overview
Create a Python script using the Diagrams library to generate a visual architecture diagram for the Outfit Manager FastAPI application.

## Requirements

### Script Location
- Place the script in the `utilities/` directory
- Name: `create_architecture_diagram.py`
- Output diagram to the `docs/` directory

### Application Architecture Analysis

The Outfit Manager is a FastAPI-based web application with the following structure:

#### Core Application
- **FastAPI App** (`main.py`): Main application entry point
- **Database**: SQLite database (`outfit_manager.db`)
- **ORM**: SQLModel for database models and relationships

#### API Routers
- `components.py`: Manages individual clothing items
- `outfits.py`: Manages collections of components
- `pieces.py`: Manages clothing categories
- `vendors.py`: Manages shopping sources
- `images.py`: Handles image uploads and processing

#### Data Models (SQLModel)
- **Vendor**: Shopping sources with components relationship
- **Piece**: Clothing categories with components relationship  
- **Component**: Individual clothing items with vendor/piece relationships
- **Outfit**: Collections of components with score and cost tracking
- **Out2Comp**: Many-to-many relationship table between outfits and components

#### Services
- **ImageService**: PIL-based image processing and validation
- **TemplateService**: Jinja2 template rendering
- **SeedDataService**: Initial data population

#### Frontend/Templates
- **Static Files**: CSS, JavaScript, images in `static/` directory
- **Jinja2 Templates**: HTML templates in `templates/` directory
- **HTMX Integration**: Dynamic frontend interactions

## Diagram Requirements

### Visual Structure
1. **Client Layer**: Web browser with HTMX
2. **Application Layer**: FastAPI app with routers
3. **Services Layer**: Image, template, and seed services
4. **Data Layer**: SQLModel models and SQLite database
5. **Static Assets**: CSS, JS, and image files
6. **Templates**: Jinja2 template files

### Relationships to Show
- Client requests to FastAPI app
- App routing to individual routers
- Router dependencies on services
- Service interactions with data models
- Model relationships with database
- Template service connections to template files
- Static file serving

### Technical Considerations
- Use appropriate diagrams library icons
- Handle potential import issues (e.g., Sqlite vs Postgresql icons)
- Include error handling and success messaging
- Generate PNG output with clear labels
- Use clusters to group related components

## Expected Output
- Clear, readable architecture diagram showing data flow
- Proper grouping of components by layer/responsibility
- Visual representation of the many-to-many relationships
- Output saved as `outfit_manager_architecture.png` in docs directory