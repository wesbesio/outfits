Core Philosophy Change:

Remove modals entirely - they're causing all the problems
Use HTMX for full page transitions - more reliable and smoother
Forms as full pages - integrated with navigation, not overlays
Consistent page structure - header and footer always present

🔧 Architecture Changes:
1. Remove Modal System Completely

❌ Delete all modal CSS and JavaScript
❌ Remove modal container from base template
❌ Remove all showModal() calls

2. HTMX-First Approach

✅ All navigation uses hx-get + hx-target="#main-content"
✅ Forms render as full pages within main content area
✅ Use hx-push-url="true" for proper URLs and back button
✅ Smooth page transitions without JavaScript complexity

3. Template Structure

Base Template (always present)
├── Header Navigation (Outfits | Components)
├── Main Content Area (#main-content)
│   ├── List Views (outfit/component grids)
│   ├── Detail Views (view/edit individual items)  
│   ├── Form Views (create new items)
│   └── Home/Welcome screen
└── Bottom Navigation (Add buttons always visible)

4. Navigation Flow

Add Outfit → Full page form at /outfits/new
Add Component → Full page form at /components/new
View Lists → Grid view in main content area
Edit Items → Full page edit form
Form Cancel → Back to appropriate list view

5. URL Structure

/ → Home page
/outfits → Outfits list
/outfits/new → New outfit form (full page)
/outfits/123 → Outfit detail view
/outfits/123/edit → Edit outfit form
/components → Components list
/components/new → New component form (full page)

6. Form Design

Centered in main content with proper spacing
Include navigation context (breadcrumbs)
Cancel buttons return to appropriate list
Submit via HTMX → redirect to list on success

🎨 Visual Design:

Header/footer always visible - consistent navigation
Forms look like integrated pages - not popup overlays
Smooth HTMX transitions - no jarring page reloads
Mobile-responsive - forms work well on all devices

✅ Benefits of This Approach:

No JavaScript modal complexity - HTMX handles everything
Proper URL handling - each form has its own URL
Browser back button works - natural navigation
Mobile-friendly - no modal sizing issues
Consistent UX - all views follow same pattern
Easier to debug - simpler architecture