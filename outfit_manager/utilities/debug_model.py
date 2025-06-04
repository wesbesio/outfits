# File: utilities/debug_model.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

def debug_models():
    """Debug SQLModel registration and field definitions."""
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("🔍 DEBUGGING MODEL REGISTRATION")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")
        
        try:
            # Import models
            from models import Component, Vendor, Piece, Outfit, Out2Comp
            from sqlmodel import SQLModel
            
            print("✅ Successfully imported all models")
            
            # Check Component model fields
            print(f"\n📋 Component model fields:")
            print(f"   Model: {Component}")
            print(f"   Table name: {Component.__tablename__ if hasattr(Component, '__tablename__') else 'default'}")
            
            # Get all fields from the Component model
            if hasattr(Component, '__fields__'):
                fields = Component.__fields__
                print(f"   Fields: {list(fields.keys())}")
                
                # Check if pieceid is in the fields
                if 'pieceid' in fields:
                    print(f"   ✅ pieceid found: {fields['pieceid']}")
                else:
                    print(f"   ❌ pieceid NOT found in model fields")
            
            # Check SQLModel metadata
            print(f"\n🗃️  SQLModel metadata tables:")
            for table_name, table in SQLModel.metadata.tables.items():
                print(f"   Table: {table_name}")
                print(f"   Columns: {[col.name for col in table.columns]}")
                
                if table_name == 'component':
                    print(f"   Component table columns: {[col.name for col in table.columns]}")
                    if any(col.name == 'pieceid' for col in table.columns):
                        print(f"   ✅ pieceid found in metadata")
                    else:
                        print(f"   ❌ pieceid NOT found in metadata")
                        
                if table_name == 'outfit':
                    print(f"   Outfit table columns: {[col.name for col in table.columns]}")
                    if any(col.name == 'score' for col in table.columns):
                        print(f"   ✅ score found in metadata")
                    else:
                        print(f"   ❌ score NOT found in metadata")
            
            # Check model annotations
            print(f"\n📝 Component model annotations:")
            if hasattr(Component, '__annotations__'):
                annotations = Component.__annotations__
                print(f"   Annotations: {list(annotations.keys())}")
                if 'pieceid' in annotations:
                    print(f"   ✅ pieceid annotation: {annotations['pieceid']}")
                else:
                    print(f"   ❌ pieceid NOT in annotations")
            
            # Check Outfit model annotations
            print(f"\n📝 Outfit model annotations:")
            if hasattr(Outfit, '__annotations__'):
                outfit_annotations = Outfit.__annotations__
                print(f"   Annotations: {list(outfit_annotations.keys())}")
                if 'score' in outfit_annotations:
                    print(f"   ✅ score annotation: {outfit_annotations['score']}")
                else:
                    print(f"   ❌ score NOT in annotations")
                if 'vendorid' in outfit_annotations:
                    print(f"   ⚠️  vendorid still in annotations: {outfit_annotations['vendorid']}")
                else:
                    print(f"   ✅ vendorid correctly removed from annotations")
            
            # Check all model relationships
            print(f"\n🔗 MODEL RELATIONSHIPS:")
            
            # Component relationships
            print(f"   Component relationships:")
            for attr_name in dir(Component):
                attr = getattr(Component, attr_name)
                if hasattr(attr, '__class__') and 'Relationship' in str(attr.__class__):
                    print(f"     - {attr_name}: {attr}")
            
            # Outfit relationships
            print(f"   Outfit relationships:")
            for attr_name in dir(Outfit):
                attr = getattr(Outfit, attr_name)
                if hasattr(attr, '__class__') and 'Relationship' in str(attr.__class__):
                    print(f"     - {attr_name}: {attr}")
            
            # Check field types and constraints
            print(f"\n📊 FIELD DETAILS:")
            
            models_to_check = [
                ('Component', Component),
                ('Outfit', Outfit),
                ('Vendor', Vendor),
                ('Piece', Piece),
                ('Out2Comp', Out2Comp)
            ]
            
            for model_name, model_class in models_to_check:
                print(f"\n   {model_name} field details:")
                if hasattr(model_class, '__annotations__'):
                    annotations = model_class.__annotations__
                    for field_name, field_type in annotations.items():
                        # Try to get the field info if it exists
                        try:
                            field_info = getattr(model_class, field_name, None)
                            if hasattr(field_info, 'field_info'):
                                constraints = []
                                if hasattr(field_info.field_info, 'max_length') and field_info.field_info.max_length:
                                    constraints.append(f"max_length={field_info.field_info.max_length}")
                                if hasattr(field_info.field_info, 'foreign_key') and field_info.field_info.foreign_key:
                                    constraints.append(f"FK: {field_info.field_info.foreign_key}")
                                if hasattr(field_info.field_info, 'primary_key') and field_info.field_info.primary_key:
                                    constraints.append("PRIMARY KEY")
                                if hasattr(field_info.field_info, 'default') and field_info.field_info.default is not None:
                                    constraints.append(f"default={field_info.field_info.default}")
                                
                                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                                print(f"     - {field_name}: {field_type}{constraint_str}")
                            else:
                                print(f"     - {field_name}: {field_type}")
                        except Exception as e:
                            print(f"     - {field_name}: {field_type} (error getting details: {e})")
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_model_creation():
    """Test creating instances of each model."""
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print(f"\n🧪 TESTING MODEL CREATION")
        print("=" * 30)
        
        try:
            from models import Component, Vendor, Piece, Outfit, Out2Comp
            
            # Test Vendor creation
            vendor = Vendor(name="Test Vendor", description="Test Description")
            print(f"✅ Vendor created: {vendor.name}")
            
            # Test Piece creation
            piece = Piece(name="Test Piece", description="Test Description")
            print(f"✅ Piece created: {piece.name}")
            
            # Test Component creation
            component = Component(
                name="Test Component",
                brand="Test Brand",
                cost=1000,
                description="Test Description",
                notes="Test Notes",
                vendorid=1,
                pieceid=1
            )
            print(f"✅ Component created: {component.name}")
            print(f"   - Has pieceid: {hasattr(component, 'pieceid')} (value: {getattr(component, 'pieceid', 'N/A')})")
            
            # Test Outfit creation
            outfit = Outfit(
                name="Test Outfit",
                description="Test Description",
                notes="Test Notes",
                totalcost=5000,
                score=3
            )
            print(f"✅ Outfit created: {outfit.name}")
            print(f"   - Has score: {hasattr(outfit, 'score')} (value: {getattr(outfit, 'score', 'N/A')})")
            print(f"   - Has vendorid: {hasattr(outfit, 'vendorid')} (should be False)")
            
            # Test Out2Comp creation
            out2comp = Out2Comp(outid=1, comid=1)
            print(f"✅ Out2Comp created: outid={out2comp.outid}, comid={out2comp.comid}")
            
        except Exception as e:
            print(f"❌ Model creation test failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    debug_models()
    test_model_creation()