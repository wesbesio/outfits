# File: routers/components.py
# Revision: 4.4 - Fix component outfits endpoint

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime
import traceback
from models.database import get_session
from models import (
    Component, ComponentCreate, ComponentUpdate, ComponentResponse,
    Vendor, Piece, Outfit, Out2Comp
)
from services.image_service import ImageService
from models import Outfit, Out2Comp


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=Union[List[ComponentResponse], HTMLResponse])
async def get_components(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    sort_by: str = "name",
    filter_vendor: Optional[int] = None,
    filter_piece: Optional[int] = None,
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of components with optional filtering and sorting"""
    # Debug information
    print(f"GET /api/components request received")
    print(f"Headers: Accept={accept}")
    print(f"Query params: sort_by={sort_by}, active_only={active_only}")
    print(f"Filter params: vendor={filter_vendor}, piece={filter_piece}")
    
    query = select(Component)
    
    # Apply filters
    if active_only:
        query = query.where(Component.active == True)
    
    if filter_vendor:
        query = query.where(Component.vendorid == filter_vendor)
    
    if filter_piece:
        query = query.where(Component.piecid == filter_piece)
    
    # Apply sorting
    if sort_by == "cost":
        query = query.order_by(Component.cost.desc())
    elif sort_by == "brand":
        query = query.order_by(Component.brand)
    elif sort_by == "created":
        query = query.order_by(Component.creation.desc())
    elif sort_by == "modified":
        query = query.order_by(Component.modified.desc())
    else:  # Default to name
        query = query.order_by(Component.name)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    components = session.exec(query).all()
    
    # Prepare component responses with additional data
    component_responses = []
    for component in components:
        component_response = ComponentResponse(
            **component.model_dump(),
            has_image=component.image is not None,
            vendor_name=component.vendor.name if component.vendor else None,
            piece_name=component.piece.name if component.piece else None
        )
        component_responses.append(component_response)
    
    # Determine if we need to return HTML or JSON
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    print(f"Is HTMX request: {is_htmx_request}, Wants HTML: {wants_html}")
    
    if is_htmx_request or wants_html:
        print("Returning HTML response")
        # Return HTML content from template
        content = templates.get_template("partials/component_cards.html").render({
            "request": request, 
            "components": component_responses
        })
        return HTMLResponse(content=content)
    else:
        print("Returning JSON response")
        # Return JSON response
        return component_responses
        # File: routers/components.py
# Revision: 4.3 - Add endpoint for component outfits and fix HTML rendering

# Add this new endpoint at the end of the file:

@router.get("/{component_id}/outfits", response_class=HTMLResponse)
async def get_component_outfits_html(
    request: Request,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get outfits that use this component as HTML"""
    # Check if component exists
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Get outfits that include this component
    outfits_query = select(Outfit).join(Out2Comp).where(
        Out2Comp.comid == component_id,
        Out2Comp.active == True
    )
    outfits = session.exec(outfits_query).all()
    
    # Enhance outfits with additional information
    enhanced_outfits = []
    for outfit in outfits:
        enhanced_outfits.append({
            "outid": outfit.outid,
            "name": outfit.name,
            "has_image": outfit.image is not None,
            "totalcost": outfit.totalcost
        })
    
    # Return HTML template
    return templates.TemplateResponse("partials/component_outfits.html", {
        "request": request,
        "component": component,
        "outfits": enhanced_outfits,
        "has_outfits": len(enhanced_outfits) > 0
    })



# Add this to the end of the file:

@router.get("/{component_id}/outfits", response_class=HTMLResponse)
async def get_component_outfits(
    request: Request,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get outfits that use this component as HTML"""
    try:
        # Check if component exists
        component = session.get(Component, component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Get outfits that include this component
        outfits_query = select(Outfit).join(Out2Comp).where(
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
        outfits = session.exec(outfits_query).all()
        
        # Enhance outfits with additional information
        enhanced_outfits = []
        for outfit in outfits:
            # Get components for this outfit to calculate cost
            components_query = select(Component).join(Out2Comp).where(
                Out2Comp.outid == outfit.outid,
                Out2Comp.active == True
            )
            components = session.exec(components_query).all()
            calculated_cost = sum(comp.cost for comp in components)
            
            enhanced_outfits.append({
                "outid": outfit.outid,
                "name": outfit.name,
                "has_image": outfit.image is not None,
                "calculated_cost": calculated_cost
            })
        
        # Return HTML partial
        if not enhanced_outfits:
            # No outfits found - return empty state
            return """
            <div class="empty-state smaller">
                <div class="empty-content">
                    <span class="empty-icon">👗</span>
                    <h3>Not used in any outfits</h3>
                    <p>This component isn't part of any outfits yet.</p>
                </div>
            </div>
            <style>
            .empty-state.smaller {
                min-height: 150px;
                padding: var(--spacing-lg);
            }
            .empty-state.smaller .empty-icon {
                font-size: 2.5rem;
                margin-bottom: var(--spacing-sm);
            }
            .empty-state.smaller h3 {
                font-size: 1.25rem;
            }
            .empty-state.smaller p {
                font-size: 0.875rem;
            }
            </style>
            """
        
        # Return outfit cards
        html = '<div class="outfit-cards">'
        for outfit in enhanced_outfits:
            html += f'''
            <div class="outfit-card-mini" 
                 hx-get="/outfits/{outfit['outid']}" 
                 hx-target="#main-content" 
                 hx-push-url="true">
                <div class="outfit-card-image">
                    {'<img src="/api/images/outfit/' + str(outfit['outid']) + '?thumbnail=true" alt="' + outfit['name'] + '" loading="lazy">' if outfit['has_image'] else '<div class="card-image-placeholder mini">👗</div>'}
                </div>
                <div class="outfit-card-content">
                    <h4 class="outfit-card-title">{outfit['name']}</h4>
                    <span class="outfit-card-cost">${outfit['calculated_cost']}</span>
                </div>
            </div>
            '''
        html += '</div>'
        
        # Add styles
        html += '''
        <style>
        .outfit-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: var(--spacing-md);
        }
        .outfit-card-mini {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-normal);
            cursor: pointer;
            border: 1px solid rgba(139, 92, 246, 0.1);
        }
        .outfit-card-mini:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }
        .outfit-card-image {
            height: 120px;
            overflow: hidden;
        }
        .outfit-card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .card-image-placeholder.mini {
            height: 100%;
            font-size: 2rem;
        }
        .outfit-card-content {
            padding: var(--spacing-md);
        }
        .outfit-card-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: var(--spacing-xs);
            color: var(--text-primary);
        }
        .outfit-card-cost {
            color: var(--primary-color);
            font-weight: 600;
        }
        </style>
        '''
        
        return HTMLResponse(content=html)
        
    except Exception as e:
        print(f"Error in get_component_outfits: {str(e)}")
        traceback.print_exc()
        return HTMLResponse("<div>Error loading outfits</div>")

        # Add this endpoint at the end of the file:
@router.get("/{component_id}/outfits", response_class=HTMLResponse)
async def get_component_outfits(
    request: Request,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get outfits that use this component as HTML"""
    try:
        # Check if component exists
        component = session.get(Component, component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Print debug info
        print(f"Fetching outfits for component {component_id}: {component.name}")
        
        # Get outfits that include this component
        outfits_query = select(Outfit).join(Out2Comp).where(
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
        outfits = session.exec(outfits_query).all()
        
        print(f"Found {len(outfits)} outfits for component {component_id}")
        
        # If no outfits, return empty state
        if not outfits:
            return HTMLResponse("""
            <div class="empty-state smaller">
                <div class="empty-content">
                    <span class="empty-icon">👗</span>
                    <h3>Not used in any outfits</h3>
                    <p>This component isn't part of any outfits yet.</p>
                </div>
            </div>
            <style>
                .empty-state.smaller {
                    min-height: 150px;
                    padding: var(--spacing-lg);
                }
                .empty-state.smaller .empty-icon {
                    font-size: 2.5rem;
                    margin-bottom: var(--spacing-sm);
                }
                .empty-state.smaller h3 {
                    font-size: 1.25rem;
                }
                .empty-state.smaller p {
                    font-size: 0.875rem;
                }
            </style>
            """)
        
        # Build HTML for outfit cards
        html = '<div class="outfit-cards">'
        
        for outfit in outfits:
            # Simple outfit display
            html += f'''
            <div class="outfit-card-mini" 
                 hx-get="/outfits/{outfit.outid}" 
                 hx-target="#main-content" 
                 hx-push-url="true">
                <div class="outfit-card-image">
                    {f'<img src="/api/images/outfit/{outfit.outid}?thumbnail=true" alt="{outfit.name}" loading="lazy">' if outfit.image else '<div class="card-image-placeholder mini">👗</div>'}
                </div>
                <div class="outfit-card-content">
                    <h4 class="outfit-card-title">{outfit.name}</h4>
                    <span class="outfit-card-cost">${outfit.totalcost}</span>
                </div>
            </div>
            '''
        
        html += '</div>'
        
        # Add styles
        html += '''
        <style>
            .outfit-cards {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: var(--spacing-md);
            }
            .outfit-card-mini {
                background: var(--card-bg);
                border-radius: var(--radius-lg);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                transition: all var(--transition-normal);
                cursor: pointer;
                border: 1px solid rgba(139, 92, 246, 0.1);
            }
            .outfit-card-mini:hover {
                transform: translateY(-4px);
                box-shadow: var(--shadow-lg);
                border-color: var(--primary-color);
            }
            .outfit-card-image {
                height: 120px;
                overflow: hidden;
            }
            .outfit-card-image img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .card-image-placeholder.mini {
                height: 100%;
                font-size: 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--accent-color) 0%, #E0E7FF 100%);
            }
            .outfit-card-content {
                padding: var(--spacing-md);
            }
            .outfit-card-title {
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: var(--spacing-xs);
                color: var(--text-primary);
            }
            .outfit-card-cost {
                color: var(--primary-color);
                font-weight: 600;
            }
        </style>
        '''
        
        return HTMLResponse(content=html)
    
    except Exception as e:
        print(f"Error in get_component_outfits: {str(e)}")
        traceback.print_exc()
        return HTMLResponse("""
        <div class="error-state">
            <div class="error-icon">⚠️</div>
            <h3>Error loading outfits</h3>
            <p>There was a problem loading outfits for this component.</p>
        </div>
        <style>
            .error-state {
                background: #FEF2F2;
                border: 1px solid #F87171;
                border-radius: var(--radius-md);
                padding: var(--spacing-lg);
                text-align: center;
                color: #B91C1C;
            }
            .error-icon {
                font-size: 2rem;
                margin-bottom: var(--spacing-sm);
            }
        </style>
        """)

        # Add this endpoint at the end of the file:
@router.get("/{component_id}/outfits", response_class=HTMLResponse)
async def get_component_outfits(
    request: Request,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get outfits that use this component as HTML"""
    try:
        # Print detailed debug info
        print(f"DEBUG: Fetching outfits for component ID: {component_id}")
        
        # Check if component exists
        component = session.get(Component, component_id)
        if not component:
            print(f"DEBUG: Component {component_id} not found")
            raise HTTPException(status_code=404, detail="Component not found")
        
        print(f"DEBUG: Component found: {component.name}")
        
        # Return a simple static message for now to verify the endpoint works
        return HTMLResponse("""
        <div class="empty-state smaller">
            <div class="empty-content">
                <span class="empty-icon">👗</span>
                <h3>Outfits Section</h3>
                <p>This component isn't used in any outfits yet.</p>
            </div>
        </div>
        <style>
            .empty-state.smaller {
                min-height: 150px;
                padding: var(--spacing-lg);
            }
            .empty-state.smaller .empty-icon {
                font-size: 2.5rem;
                margin-bottom: var(--spacing-sm);
            }
            .empty-state.smaller h3 {
                font-size: 1.25rem;
            }
            .empty-state.smaller p {
                font-size: 0.875rem;
            }
        </style>
        """)
    
    except Exception as e:
        print(f"ERROR in get_component_outfits: {str(e)}")
        traceback.print_exc()
        return HTMLResponse("""
        <div class="error-state">
            <div class="error-icon">⚠️</div>
            <h3>Error loading outfits</h3>
            <p>There was a problem loading outfits for this component.</p>
            <pre style="text-align: left; font-size: 0.8rem; color: #666; overflow: auto; max-height: 200px; padding: 0.5rem; background: #f5f5f5; border-radius: 0.25rem;">""" + 
            str(traceback.format_exc()) + 
            """</pre>
        </div>
        <style>
            .error-state {
                background: #FEF2F2;
                border: 1px solid #F87171;
                border-radius: var(--radius-md);
                padding: var(--spacing-lg);
                text-align: center;
                color: #B91C1C;
            }
            .error-icon {
                font-size: 2rem;
                margin-bottom: var(--spacing-sm);
            }
        </style>
        """)