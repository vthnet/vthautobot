import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

FORCE_JOIN_CHANNEL = os.getenv("FORCE_JOIN_CHANNEL")

# ==========================================
# Database
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")

# ==========================================
# CheapestSMM Panel
# ==========================================

PANEL_URL = "https://cheapestsmmpanels.com/api/v2"
PANEL_KEY = os.getenv("PANEL_KEY")

VIEW_SERVICE = 344
REACTION_SERVICE = 3960

# ==========================================
# Credits
# ==========================================

REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "50"))
CREDITS_PER_RUPEE = int(os.getenv("CREDITS_PER_RUPEE", "50"))

VIEW_COST = int(os.getenv("VIEW_COST", "1"))
REACTION_COST = int(os.getenv("REACTION_COST", "1"))

# ==========================================
# Channel Limits
# ==========================================

MIN_VIEWS = 20
MAX_VIEWS = 9000

MIN_REACTIONS = 20
MAX_REACTIONS = 5000