from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)

if 'Inventory_Master' in tables:
    columns = inspector.get_columns('Inventory_Master')
    print('\nInventory_Master columns:')
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
else:
    print('\nInventory_Master table not found')
