# File: debug_models.py
# Revision: 1.0 - Debug model registration and field definitions

def debug_models():
    """Debug SQLModel registration and field definitions."""
    print("🔍 DEBUGGING MODEL REGISTRATION")
    print("=" * 50)
    
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
        
        # Check model annotations
        print(f"\n📝 Component model annotations:")
        if hasattr(Component, '__annotations__'):
            annotations = Component.__annotations__
            print(f"   Annotations: {list(annotations.keys())}")
            if 'pieceid' in annotations:
                print(f"   ✅ pieceid annotation: {annotations['pieceid']}")
            else:
                print(f"   ❌ pieceid NOT in annotations")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_models() 