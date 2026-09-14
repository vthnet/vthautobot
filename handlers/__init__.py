from .start import router as start_router
from .wallet import router as wallet_router
from .channels import router as channels_router
from .admin import router as admin_router
from .referral import router as referral_router
from .settings import router as settings_router
from .broadcast import router as broadcast_router
from .orders import router as orders_router
from .stats import router as stats_router

routers = (
    start_router,
    wallet_router,
    channels_router,
    admin_router,
    referral_router,
     settings_router,
     broadcast_router,
     orders_router,
     stats_router
)