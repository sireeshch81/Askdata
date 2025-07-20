# Import routers from endpoint modules
from endpoints.data_management import router as data_management_router

# Export all routers
__all__ = ['data_management_router']
