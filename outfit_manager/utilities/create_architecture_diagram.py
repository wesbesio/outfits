#!/usr/bin/env python3
"""
Architecture Diagram Generator for Outfit Manager
Creates a visual diagram of the FastAPI application architecture using the Diagrams library.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import Fastapi
from diagrams.programming.language import Python
from diagrams.custom import Custom
from diagrams.onprem.client import Client
from diagrams.programming.flowchart import Document
from diagrams.onprem.compute import Server
from diagrams.aws.storage import S3

def create_outfit_manager_diagram():
    """Generate architecture diagram for the Outfit Manager application."""
    
    # Set output directory to docs
    output_path = "../docs/outfit_manager_architecture"
    
    with Diagram("Outfit Manager Architecture", 
                 filename=output_path, 
                 show=False, 
                 direction="TB"):
        
        # Client Layer
        with Cluster("Client Layer"):
            browser = Client("Web Browser")
            htmx = Document("HTMX")
            
        # Application Layer
        with Cluster("FastAPI Application"):
            app = Fastapi("main.py\n(FastAPI App)")
            
            # Routers
            with Cluster("API Routers"):
                components_router = Python("components.py")
                outfits_router = Python("outfits.py")
                pieces_router = Python("pieces.py")
                vendors_router = Python("vendors.py")
                images_router = Python("images.py")
                
        # Services Layer
        with Cluster("Services"):
            image_service = Server("Image Service\n(PIL/Image Processing)")
            template_service = Server("Template Service\n(Jinja2)")
            seed_service = Server("Seed Data Service")
            
        # Models & Database Layer
        with Cluster("Data Layer"):
            with Cluster("SQLModel Models"):
                vendor_model = Python("Vendor")
                piece_model = Python("Piece")
                component_model = Python("Component")
                outfit_model = Python("Outfit")
                out2comp_model = Python("Out2Comp\n(Many-to-Many)")
                
            database = Custom("SQLite Database\n(outfit_manager.db)", "../docs/sqlite.png")
            
        # Static Files
        with Cluster("Static Assets"):
            css_files = Document("CSS Files")
            js_files = Document("JavaScript Files")
            static_images = S3("Static Images")
            
        # Template Files
        with Cluster("Templates"):
            base_template = Document("Base Templates")
            form_templates = Document("Form Templates")
            partial_templates = Document("Partial Templates")
            
        # Client to Application connections
        browser >> Edge(label="HTTP Requests") >> app
        browser >> Edge(label="HTMX Requests") >> htmx
        htmx >> app
        
        # Application to Routers
        app >> components_router
        app >> outfits_router
        app >> pieces_router
        app >> vendors_router
        app >> images_router
        
        # Routers to Services
        components_router >> image_service
        outfits_router >> image_service
        images_router >> image_service
        
        [components_router, outfits_router, pieces_router, vendors_router] >> template_service
        
        # Services to Models
        [components_router, outfits_router, pieces_router, vendors_router] >> vendor_model
        [components_router, outfits_router, pieces_router, vendors_router] >> piece_model
        [components_router, outfits_router, pieces_router, vendors_router] >> component_model
        [outfits_router, components_router] >> outfit_model
        [outfits_router, components_router] >> out2comp_model
        
        # Models to Database
        [vendor_model, piece_model, component_model, outfit_model, out2comp_model] >> database
        
        # Template Service to Templates
        template_service >> base_template
        template_service >> form_templates
        template_service >> partial_templates
        
        # Static file serving
        app >> css_files
        app >> js_files
        app >> static_images
        
        # Startup process
        app >> Edge(label="Startup") >> seed_service
        seed_service >> database

if __name__ == "__main__":
    try:
        create_outfit_manager_diagram()
        print("✅ Architecture diagram generated successfully!")
        print("📁 Output location: docs/outfit_manager_architecture.png")
    except Exception as e:
        print(f"❌ Error generating diagram: {e}")
        print("💡 Make sure the 'diagrams' library is installed: pip install diagrams")