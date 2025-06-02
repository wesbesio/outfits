# File: routers/outfits.py
# Revision: 1.7 - Manual template render test for /outfits/new HTMX path

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List
from jinja2 import TemplateNotFound # Import TemplateNotFound

from models import Outfit, Component, Vendor, Out2Comp, Piece
from models.database import get_session
from services.image_service import ImageService

router = APIRouter()
# Ensure the Jinja2Templates instance is correctly initialized
# The directory should be relative to where main.py is, or an absolute path.
# Assuming 'templates' is at the same level as 'main.py' or 'routers' directory.
try:
    templates = Jinja2Templates(directory="templates")
except Exception as e:
    print(f"Error initializing Jinja2Templates: {e}")
    # Fallback or raise, depending on desired behavior if templates can't load
    # For this test, we'll let it proceed and see if specific template loading fails.
    pass


async def get_outfit_form_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True).order_by(Vendor.name)).all()
    all_active_components = session.exec(select(Component).where(Component.active == True).order_by(Component.name)).all()
    return {"request": request, "vendors": vendors, "all_active_components": all_active_components}

@router.get("/outfits/", response_class=HTMLResponse)
async def list_outfits_page(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True).order_by(Vendor.name)).all()
    context = {"request": request, "vendors": vendors}
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("outfits/list_main_content.html", context)
    return templates.TemplateResponse("outfits/list.html", context)

@router.get("/outfits/new", response_class=HTMLResponse)
async def create_outfit_page(request: Request, context: dict = Depends(get_outfit_form_context)):
    print(f"Accessing /outfits/new. HX-Request header: {request.headers.get('hx-request')}")

    if request.headers.get("hx-request"):
        print("Attempting to serve MANUALLY RENDERED HTML for HTMX request to /outfits/new")
        
        minimal_htmx_context = {
            "request": request,
            "outfit": None, 
            "form_action": "/api/outfits/", 
            "vendors": [], 
            "error": None,
            # The 'components' variable for the checkbox list is loaded by a separate hx-get.
        }
        
        try:
            # Manually get the template
            template_to_render = templates.get_template("forms/outfit_form_content.html")
            # Manually render it
            rendered_html = template_to_render.render(minimal_htmx_context)
            
            if not rendered_html.strip():
                print("ERROR: Manually rendered HTML for 'forms/outfit_form_content.html' is EMPTY or WHITESPACE.")
                # Fallback to a very basic hardcoded HTML to ensure *something* is sent
                rendered_html = """
                <div style='border:2px solid orange; padding:10px;'>
                    <p>Manual render resulted in empty string. Fallback HTML.</p>
                    <p>Context was: {}</p>
                </div>
                """.format(minimal_htmx_context)
                return HTMLResponse(content=rendered_html, status_code=200)

            print(f"Manually rendered HTML (first 100 chars): {rendered_html[:100]}")
            return HTMLResponse(content=rendered_html)
            
        except TemplateNotFound:
            print("ERROR: Jinja2 TemplateNotFound for 'forms/outfit_form_content.html'")
            return HTMLResponse(content="<p style='color:red;'>Error: Template 'forms/outfit_form_content.html' not found by Jinja2.</p>", status_code=500)
        except Exception as e:
            print(f"ERROR: Exception during manual template rendering for 'forms/outfit_form_content.html': {e}")
            # It's crucial to see this error in the server logs.
            return HTMLResponse(content=f"<p style='color:red;'>Server error during template rendering: {e}</p>", status_code=500)

    # Full page load context
    print("Serving outfits/detail.html for full page request")
    full_page_template_vars = {
        "request": request,
        "vendors": context.get("vendors"),
        "components": context.get("all_active_components"), 
        "outfit": None,
        "edit_mode": True,
        "form_action": "/api/outfits/",
        "current_component_ids": set(),
        "error": None
    }
    return templates.TemplateResponse("outfits/detail.html", full_page_template_vars)


# ... (rest of the routes: /outfits/{outid}, /outfits/{outid}/edit, and all /api/outfits/* routes)
# These should remain the same as Revision 1.5 for now.
@router.get("/outfits/{outid}", response_class=HTMLResponse)
async def get_outfit_page(outid: int, request: Request, session: Session = Depends(get_session)):
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    outfit_component_links = session.exec(
        select(Out2Comp, Component)
        .join(Component, Out2Comp.comid == Component.comid)
        .where(Out2Comp.outid == outid, Out2Comp.active == True, Component.active == True)
    ).all()
    associated_components = sorted([link.Component for link in outfit_component_links if link.Component], key=lambda c: c.name)
    
    outfit.totalcost = sum(comp.cost for comp in associated_components if comp)

    template_vars = {
        "request": request, 
        "outfit": outfit, 
        "edit_mode": False, 
        "associated_components": associated_components
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("outfits/detail_content.html", template_vars)
    return templates.TemplateResponse("outfits/detail.html", template_vars)

@router.get("/outfits/{outid}/edit", response_class=HTMLResponse)
async def edit_outfit_page(outid: int, request: Request, context: dict = Depends(get_outfit_form_context), session: Session = Depends(get_session)):
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    current_component_ids = {
        link.comid for link in session.exec(
            select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)
        ).all()
    }
    
    template_vars = {
        "request": request,
        "vendors": context.get("vendors"),
        "components": context.get("all_active_components"), 
        "outfit": outfit, 
        "edit_mode": True, 
        "form_action": f"/api/outfits/{outid}",
        "current_component_ids": current_component_ids,
        "error": None
    }

    if request.headers.get("hx-request"):
        # Use the FULL version of the form content for edit, as it expects 'outfit' object
        return templates.TemplateResponse("forms/outfit_form_content.html", template_vars)
    return templates.TemplateResponse("outfits/detail.html", template_vars)


@router.get("/api/outfits/", response_class=HTMLResponse)
async def list_outfits_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    vendorid: Optional[int] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    query = select(Outfit).where(Outfit.active == True)
    if q:
        query = query.where(Outfit.name.ilike(f"%{q}%") | Outfit.description.ilike(f"%{q}%"))
    if vendorid:
        query = query.where(Outfit.vendorid == vendorid)

    sort_field = getattr(Outfit, sort_by, Outfit.name)
    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    outfits = session.exec(query).all()

    for outfit_item in outfits:
        active_components_links = session.exec(
            select(Out2Comp, Component)
            .join(Component, Out2Comp.comid == Component.comid)
            .where(Out2Comp.outid == outfit_item.outid, Out2Comp.active == True, Component.active == True)
        ).all()
        outfit_item.totalcost = sum(link.Component.cost for link in active_components_links if link.Component)
    return templates.TemplateResponse("outfits/list_content.html", {"request": request, "outfits": outfits})

@router.post("/api/outfits/", response_class=HTMLResponse)
async def create_outfit(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    component_ids: List[int] = Form([]) 
):
    processed_image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()
        if image_bytes: 
            processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
            if processed_image_bytes is None:
                form_context = await get_outfit_form_context(request, session)
                return templates.TemplateResponse(
                    "forms/outfit_form_content.html", # FULL form
                    {**form_context, 
                     "error": "Invalid or too large image file. Max 5MB. Allowed: JPEG, PNG, WEBP, GIF.",
                     "outfit": Outfit(name=name, description=description, notes=notes, vendorid=vendorid),
                     "components": form_context.get("all_active_components"),
                     "current_component_ids": set(component_ids), "form_action": "/api/outfits/"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    new_outfit = Outfit(
        name=name, description=description, notes=notes,
        vendorid=vendorid, image=processed_image_bytes, totalcost=0
    )
    session.add(new_outfit)
    session.commit()
    session.refresh(new_outfit)

    current_total_cost = 0
    if component_ids:
        for comid_val in component_ids:
            component_item = session.get(Component, comid_val)
            if component_item and component_item.active:
                out2comp_link = Out2Comp(outid=new_outfit.outid, comid=comid_val, active=True)
                session.add(out2comp_link)
                current_total_cost += component_item.cost
    
    new_outfit.totalcost = current_total_cost
    session.add(new_outfit)
    session.commit()
    session.refresh(new_outfit)

    response = RedirectResponse(url=f"/outfits/{new_outfit.outid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/outfits/{new_outfit.outid}"
    return response

@router.put("/api/outfits/{outid}", response_class=HTMLResponse)
async def update_outfit(
    outid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[bool] = Form(False),
    component_ids: List[int] = Form([])
):
    outfit_to_update = session.get(Outfit, outid)
    if not outfit_to_update or not outfit_to_update.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    outfit_to_update.name = name
    outfit_to_update.description = description
    outfit_to_update.notes = notes
    outfit_to_update.vendorid = vendorid

    if image and image.filename:
        image_bytes = await image.read()
        if image_bytes:
            processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
            if processed_image_bytes is None:
                form_context = await get_outfit_form_context(request, session)
                return templates.TemplateResponse(
                    "forms/outfit_form_content.html", # FULL form
                    {**form_context,
                     "error": "Invalid or too large image file. Max 5MB. Allowed: JPEG, PNG, WEBP, GIF.",
                     "outfit": outfit_to_update,
                     "components": form_context.get("all_active_components"),
                     "current_component_ids": set(component_ids), "form_action": f"/api/outfits/{outid}"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            outfit_to_update.image = processed_image_bytes
    elif not keep_existing_image:
        outfit_to_update.image = None

    existing_links = session.exec(select(Out2Comp).where(Out2Comp.outid == outid)).all()
    existing_comids_in_db = {link.comid: link for link in existing_links}
    selected_comids_from_form = set(component_ids)

    for comid_val, link_obj in existing_comids_in_db.items():
        if comid_val not in selected_comids_from_form:
            if link_obj.active:
                link_obj.active = False
                session.add(link_obj)
        else: 
            if not link_obj.active:
                link_obj.active = True
                session.add(link_obj)

    for comid_val in selected_comids_from_form:
        if comid_val not in existing_comids_in_db:
            component_item = session.get(Component, comid_val)
            if component_item and component_item.active:
                new_link = Out2Comp(outid=outid, comid=comid_val, active=True)
                session.add(new_link)
    
    session.commit() 

    active_component_links = session.exec(
        select(Out2Comp, Component)
        .join(Component, Out2Comp.comid == Component.comid)
        .where(Out2Comp.outid == outid, Out2Comp.active == True, Component.active == True)
    ).all()
    outfit_to_update.totalcost = sum(link.Component.cost for link in active_component_links if link.Component)
    
    session.add(outfit_to_update)
    session.commit()
    session.refresh(outfit_to_update)

    response = RedirectResponse(url=f"/outfits/{outfit_to_update.outid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/outfits/{outfit_to_update.outid}"
    return response

@router.delete("/api/outfits/{outid}")
async def delete_outfit(outid: int, session: Session = Depends(get_session)):
    outfit_to_delete = session.get(Outfit, outid)
    if not outfit_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    outfit_to_delete.active = False
    session.add(outfit_to_delete)
    links_to_deactivate = session.exec(select(Out2Comp).where(Out2Comp.outid == outid)).all()
    for link in links_to_deactivate:
        if link.active:
            link.active = False
            session.add(link)
    session.commit()

    response = HTMLResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = "/outfits/"
    return response

@router.get("/api/outfits/components_list", response_class=HTMLResponse)
async def get_available_components_for_outfit_form(
    request: Request,
    session: Session = Depends(get_session),
    outid: Optional[str] = Query(None) 
):
    all_active_components = session.exec(select(Component).where(Component.active == True).order_by(Component.name)).all()
    current_component_ids = set()
    numeric_outid: Optional[int] = None

    if outid is not None and outid.strip().isdigit():
        try:
            numeric_outid = int(outid.strip())
        except ValueError:
            print(f"Warning: Could not convert outid='{outid}' to int.")
            numeric_outid = None

    if numeric_outid is not None:
        outfit_exists_check = session.get(Outfit, numeric_outid)
        if outfit_exists_check:
            current_component_ids = {
                link.comid for link in session.exec(
                    select(Out2Comp).where(Out2Comp.outid == numeric_outid, Out2Comp.active == True)
                ).all()
            }
    
    return templates.TemplateResponse(
        "partials/component_checkboxes.html",
        {"request": request, "components": all_active_components, "current_component_ids": current_component_ids}
    )
