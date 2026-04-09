"""
Django settings for Help Center Backend.
Base settings shared across all environments.

Copyright (C) 2025 Pillar Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import os
import socket
import sys
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Testing mode - Controls whether running in test environment
TESTING = os.environ.get('TESTING', 'false').lower() == 'true'

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps - infrastructure
    'common.apps.CommonConfig',

    # Local apps - features
    'apps.users',                       # Authentication
    'apps.mcp',                         # MCP Server
    'apps.knowledge',                   # Knowledge sources for Product Assistant
    
    # Domain-focused apps
    'apps.products',                    # Products (core), actions, tooltips, platforms
    'apps.analytics',                   # Searches, views, sessions, chat
    'apps.identity',                    # Cross-channel identity mapping and linking

    # Server-side tools
    'apps.tools',                       # Server-side tool endpoints, MCP sources

    # OAuth
    'oauth2_provider',                  # django-oauth-toolkit (DOT)
    'apps.mcp_oauth',                   # MCP OAuth 2.1 (inbound + outbound)

    # Public tools
    'apps.agent_score',                 # Agent Readiness Score (public free tool)

    # Billing
    'apps.billing',                     # Stripe billing, usage metering, plan enforcement

    # Integrations (omnichannel)
    'encrypted_fields',                 # Fernet encryption for bot tokens
    'apps.integrations.slack',          # Slack bot integration
    'apps.integrations.discord',        # Discord bot integration
    'apps.integrations.email_channel',  # Email channel integration
]

# Internal tools (impersonation, diagnostics) — excluded from open source repo.
# Gated behind env var + try/except so open source builds don't break.
ENABLE_INTERNAL_TOOLS = os.environ.get('ENABLE_INTERNAL_TOOLS', 'false').lower() == 'true'
if ENABLE_INTERNAL_TOOLS:
    try:
        import internal  # noqa: F401
        INSTALLED_APPS += ['internal']
    except ImportError:
        pass

MIDDLEWARE = [
    # CORS must be first to handle preflight OPTIONS requests before other middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'apps.mcp.middleware.allowed_hosts.DynamicAllowedHostsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.products.middleware.CustomerIdMiddleware',  # Customer resolution
    'apps.analytics.middleware.AnalyticsMiddleware',  # Analytics
    'apps.mcp.middleware.product_resolver.ProductResolverMiddleware',  # MCP product resolution
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ASGI Application
ASGI_APPLICATION = 'config.asgi.application'

# Database
# Uses the same PostgreSQL instance as main backend (same database for now)
# Connection Pooling Strategy:
# - Cloud Run can scale horizontally
# - PostgreSQL has limited connections
# - Set CONN_MAX_AGE=0 for services that can scale
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('HC_POSTGRES_DB', 'help_center_dev'),
        'USER': os.environ.get('HC_POSTGRES_USER', 'help_center_user'),
        'PASSWORD': os.environ.get('HC_POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('HC_POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('HC_POSTGRES_PORT', '5432'),
        # CONN_MAX_AGE=0 for Cloud SQL compatibility
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '0')),
        'CONN_HEALTH_CHECKS': True,
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            **({'options': os.environ['HC_POSTGRES_OPTIONS']} if os.environ.get('HC_POSTGRES_OPTIONS') else {}),
        },
    }
}

if os.environ.get('DEV_DB_HOST'):
    DATABASES['dev_readonly'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEV_DB_NAME', 'help_center_dev'),
        'USER': os.environ.get('DEV_DB_USER', 'help_center_user'),
        'PASSWORD': os.environ.get('DEV_DB_PASSWORD', ''),
        'HOST': os.environ.get('DEV_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DEV_DB_PORT', '5433'),
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for serving static files in production
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'public_api': '100/minute',
        'public_form_minute': '5/minute',
        'public_form_hour': '15/hour',
        'public_form_day': '30/day',
        'agent_score_scan': '10/minute',
        'agent_score_signup': '10/hour',
        'headless_chat': '200/minute',
        'link_code': '10/minute',
    },
}

# Slack Configuration (internal notifications)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', None)
SLACK_ENABLED_IN_DEBUG = os.environ.get('SLACK_ENABLED_IN_DEBUG', 'false').lower() == 'true'

# Slack Bot Integration (omnichannel agent)
SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID', '')
SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET', '')
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')

# Discord Configuration
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET', '')
DISCORD_PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY', '')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')

# Fernet encryption key for bot tokens (generate with: from cryptography.fernet import Fernet; Fernet.generate_key())
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', '')
SALT_KEY = FIELD_ENCRYPTION_KEY

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# DRF Spectacular (API Documentation) Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Help Center API',
    'DESCRIPTION': 'API documentation for Help Center Backend - Standalone documentation service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SERVERS': [
        {'url': 'http://localhost:8003', 'description': 'Local development server'},
    ],
    'SECURITY': [
        {
            'bearerAuth': []
        }
    ],
    'COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'tryItOutEnabled': True,
    },
}

# CORS Settings
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# TCP keepalive options to detect dead connections before the app tries to use
# them. These constants are Linux-only; macOS uses a different API.
if sys.platform == "linux":
    _REDIS_KEEPALIVE_OPTS = {
        socket.TCP_KEEPIDLE: 60,
        socket.TCP_KEEPINTVL: 15,
        socket.TCP_KEEPCNT: 3,
    }
else:
    _REDIS_KEEPALIVE_OPTS = {}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'SOCKET_KEEPALIVE': True,
            'SOCKET_KEEPALIVE_OPTIONS': _REDIS_KEEPALIVE_OPTS,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'health_check_interval': 30,
            },
        },
        'KEY_PREFIX': 'help_center',
        'TIMEOUT': 300,
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Channel Layers for WebSocket support
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# ==============================================================================
# HATCHET CONFIGURATION (for background tasks)
# ==============================================================================
# HC_HATCHET_* vars allow backend to use a separate Hatchet tenant from main backend
HATCHET_ENABLED = os.environ.get('HC_HATCHET_ENABLED', os.environ.get('HATCHET_ENABLED', 'true')).lower() == 'true'
HATCHET_CLIENT_TOKEN = os.environ.get('HC_HATCHET_CLIENT_TOKEN', os.environ.get('HATCHET_CLIENT_TOKEN', ''))
HATCHET_SERVER_URL = os.environ.get('HC_HATCHET_SERVER_URL', os.environ.get('HATCHET_SERVER_URL', 'https://app.hatchet.run'))
HATCHET_NAMESPACE = os.environ.get('HC_HATCHET_NAMESPACE', os.environ.get('HATCHET_NAMESPACE', 'help-center'))

# Task Execution Backend
TASK_EXECUTION_BACKEND = os.environ.get('TASK_EXECUTION_BACKEND', 'hatchet')

# ==============================================================================
# STRIPE BILLING CONFIGURATION
# ==============================================================================
_stripe_live = os.environ.get('STRIPE_LIVE_MODE', 'False').lower() in ('true', '1')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or os.environ.get(
    'STRIPE_LIVE_SECRET_KEY' if _stripe_live else 'STRIPE_TEST_SECRET_KEY', ''
)
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') or os.environ.get(
    'STRIPE_LIVE_PUBLISHABLE_KEY' if _stripe_live else 'STRIPE_TEST_PUBLISHABLE_KEY', ''
)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_PRICE_IDS = {
    'hobby_monthly': os.environ.get('STRIPE_PRICE_HOBBY_MONTHLY', ''),
    'hobby_yearly': os.environ.get('STRIPE_PRICE_HOBBY_YEARLY', ''),
    'pro_monthly': os.environ.get('STRIPE_PRICE_PRO_MONTHLY', ''),
    'pro_yearly': os.environ.get('STRIPE_PRICE_PRO_YEARLY', ''),
    'growth_monthly': os.environ.get('STRIPE_PRICE_GROWTH_MONTHLY', ''),
    'growth_yearly': os.environ.get('STRIPE_PRICE_GROWTH_YEARLY', ''),
}
STRIPE_OVERAGE_PRICE_IDS = {
    'hobby': os.environ.get('STRIPE_PRICE_HOBBY_OVERAGE', ''),
    'pro': os.environ.get('STRIPE_PRICE_PRO_OVERAGE', ''),
    'growth': os.environ.get('STRIPE_PRICE_GROWTH_OVERAGE', ''),
}
STRIPE_METER_EVENT_NAME = os.environ.get('STRIPE_METER_EVENT_NAME', 'agent_response')

# ==============================================================================
# POSTHOG CONFIGURATION (Feature Flags & Analytics)
# ==============================================================================
POSTHOG_API_KEY = os.environ.get('POSTHOG_API_KEY', '')
POSTHOG_HOST = os.environ.get('POSTHOG_HOST', 'https://us.i.posthog.com')
POSTHOG_ENABLED = os.environ.get('POSTHOG_ENABLED', 'true').lower() == 'true'

# ==============================================================================
# AGNOST AI CONFIGURATION (Conversation Analytics)
# ==============================================================================
AGNOST_ORG_ID = os.environ.get('AGNOST_ORG_ID', '')

# Local override for master flag
HATCHET_ENABLE_ALL_TASKS_LOCAL = os.environ.get('HATCHET_ENABLE_ALL_TASKS_LOCAL', 'false').lower() == 'true'

# ==============================================================================
# STORAGE CONFIGURATION
# ==============================================================================
STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')  # 'local', 's3', or 'gcs'

# GCS Configuration
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', 'pillar-storage')
GS_BUCKET_DOCUMENTS = os.environ.get('GCS_BUCKET_DOCUMENTS', 'pillar-storage')
GCS_BUCKET_PUBLIC = os.environ.get('GCS_BUCKET_PUBLIC', 'pillar-prod-public')
GS_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', os.environ.get('GS_PROJECT_ID', ''))

# Article images use public bucket (no signed URLs needed)
ARTICLE_IMAGES_BUCKET = os.environ.get('ARTICLE_IMAGES_BUCKET', GCS_BUCKET_PUBLIC)

# Conversation Image Upload Settings
MAX_CONVERSATION_IMAGE_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONVERSATION_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic', 'heif']

# ==============================================================================
# LLM CONFIGURATION (for AI features)
# ==============================================================================
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
DEFAULT_LLM_MODEL = os.environ.get('DEFAULT_LLM_MODEL', 'anthropic/flagship')
DEFAULT_VISION_MODEL = os.environ.get('DEFAULT_VISION_MODEL', 'anthropic/flagship')

# ==============================================================================
# RAG CONFIGURATION (for search/embeddings)
# ==============================================================================
RAG_EMBEDDING_MODEL = os.environ.get('RAG_EMBEDDING_MODEL', 'gemini-embedding-001')
RAG_EMBEDDING_DIMENSIONS = int(os.environ.get('RAG_EMBEDDING_DIMENSIONS', '1536'))
RAG_EMBEDDING_PROVIDER = os.environ.get('RAG_EMBEDDING_PROVIDER', 'google')
RAG_EMBEDDING_VERSION = os.environ.get('RAG_EMBEDDING_VERSION', 'v1.0')

# Chunking Strategy
RAG_CHUNK_SIZE = int(os.environ.get('RAG_CHUNK_SIZE', '1024'))
RAG_CHUNK_OVERLAP = int(os.environ.get('RAG_CHUNK_OVERLAP', '200'))
RAG_BATCH_SIZE = int(os.environ.get('RAG_BATCH_SIZE', '50'))
RAG_ASYNC_INDEXING = os.environ.get('RAG_ASYNC_INDEXING', 'true').lower() == 'true'
RAG_MAX_CHUNKS_PER_URL = int(os.environ.get('RAG_MAX_CHUNKS_PER_URL', '5'))

# Retrieval Settings
RAG_DEFAULT_TOP_K = int(os.environ.get('RAG_DEFAULT_TOP_K', '5'))
RAG_SIMILARITY_THRESHOLD = float(os.environ.get('RAG_SIMILARITY_THRESHOLD', '0.5'))
KEYWORD_SEARCH_USE_SEMANTIC_FALLBACK = os.environ.get('KEYWORD_SEARCH_USE_SEMANTIC_FALLBACK', 'true').lower() == 'true'
KEYWORD_SEARCH_SEMANTIC_TOP_K = int(os.environ.get('KEYWORD_SEARCH_SEMANTIC_TOP_K', '10'))

# Metadata Extraction Settings
RAG_EXTRACT_TITLES = os.environ.get('RAG_EXTRACT_TITLES', 'true').lower() == 'true'
RAG_EXTRACT_KEYWORDS = os.environ.get('RAG_EXTRACT_KEYWORDS', 'true').lower() == 'true'
RAG_EXTRACT_ENTITIES = os.environ.get('RAG_EXTRACT_ENTITIES', 'false').lower() == 'true'
RAG_EXTRACT_QUESTIONS = os.environ.get('RAG_EXTRACT_QUESTIONS', 'false').lower() == 'true'

# Cohere Reranking Configuration
COHERE_API_KEY = os.environ.get('COHERE_API_KEY', '')
COHERE_RERANK_ENABLED = os.environ.get('COHERE_RERANK_ENABLED', 'true').lower() == 'true'
COHERE_RERANK_MODEL = os.environ.get('COHERE_RERANK_MODEL', 'rerank-v3.5')
COHERE_RERANK_TOP_N = int(os.environ.get('COHERE_RERANK_TOP_N', '5'))
COHERE_RERANK_CANDIDATES = int(os.environ.get('COHERE_RERANK_CANDIDATES', '15'))

# Quality Thresholds
RERANK_QUALITY_RATIO = float(os.environ.get('RERANK_QUALITY_RATIO', '0.80'))
VECTOR_QUALITY_RATIO = float(os.environ.get('VECTOR_QUALITY_RATIO', '0.90'))

# Action Search Configuration
# Uses top-k + percentage-of-top strategy instead of hard thresholds
ACTION_SEARCH_CANDIDATES = int(os.environ.get('ACTION_SEARCH_CANDIDATES', '15'))
ACTION_SEARCH_TOP_N = int(os.environ.get('ACTION_SEARCH_TOP_N', '5'))
ACTION_SEARCH_MIN = int(os.environ.get('ACTION_SEARCH_MIN', '3'))
ACTION_QUALITY_RATIO = float(os.environ.get('ACTION_QUALITY_RATIO', '0.75'))
ACTION_RERANK_ENABLED = os.environ.get('ACTION_RERANK_ENABLED', 'true').lower() == 'true'

# ==============================================================================
# BROWSERBASE / STAGEHAND CONFIGURATION (Agent Signup Test)
# ==============================================================================
BROWSERBASE_API_KEY = os.environ.get('BROWSERBASE_API_KEY', '')
BROWSERBASE_PROJECT_ID = os.environ.get('BROWSERBASE_PROJECT_ID', '')
STAGEHAND_AGENT_MODEL = os.environ.get('STAGEHAND_AGENT_MODEL', 'google/gemini-3-flash-preview')

# ==============================================================================
# FIRECRAWL CONFIGURATION (Web scraping)
# ==============================================================================
FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', '')
FIRECRAWL_API_URL = os.environ.get('FIRECRAWL_API_URL', 'https://api.firecrawl.dev')
FIRECRAWL_WEBHOOK_SECRET = os.environ.get('FIRECRAWL_WEBHOOK_SECRET', '')

# ==============================================================================
# SOURCES CONFIGURATION (External content integrations)
# ==============================================================================
# Unified.to API (multi-provider integration layer)
UNIFIED_TO_API_KEY = os.environ.get('UNIFIED_TO_API_KEY', '')
UNIFIED_TO_WORKSPACE_ID = os.environ.get('UNIFIED_TO_WORKSPACE_ID', '')

# GitHub OAuth (for repository integration and user login)
GITHUB_OAUTH_CLIENT_ID = os.environ.get('GITHUB_OAUTH_CLIENT_ID', '')
GITHUB_OAUTH_SECRET = os.environ.get('GITHUB_OAUTH_SECRET', '')
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN', '')

# Google OAuth (for user login)
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_WEB_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_SECRET = os.environ.get('GOOGLE_WEB_OAUTH_SECRET_ID', '')

# ==============================================================================
# OAUTH 2.1 / MCP AUTHENTICATION (django-oauth-toolkit)
# ==============================================================================
OAUTH2_PROVIDER_APPLICATION_MODEL = 'mcp_oauth.MCPApplication'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'mcp_oauth.MCPAccessToken'
OAUTH2_PROVIDER_GRANT_MODEL = 'mcp_oauth.MCPGrant'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'mcp_oauth.MCPRefreshToken'
OAUTH2_PROVIDER_ID_TOKEN_MODEL = 'mcp_oauth.MCPIDToken'
OAUTH2_PROVIDER = {
    'APPLICATION_MODEL': 'mcp_oauth.MCPApplication',
    'ACCESS_TOKEN_MODEL': 'mcp_oauth.MCPAccessToken',
    'GRANT_MODEL': 'mcp_oauth.MCPGrant',
    'REFRESH_TOKEN_MODEL': 'mcp_oauth.MCPRefreshToken',
    'PKCE_REQUIRED': True,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400 * 30,
    'ALLOWED_REDIRECT_URI_SCHEMES': ['http', 'https'],
    'OAUTH2_VALIDATOR_CLASS': 'apps.mcp_oauth.validators.MCPOAuth2Validator',
}

# Webhook Configuration
WEBHOOK_BASE_URL = os.environ.get('WEBHOOK_BASE_URL', os.environ.get('API_BASE_URL', 'http://localhost:8003'))
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8003')

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('SENDGRID_SMTP_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = int(os.environ.get('SENDGRID_SMTP_PORT', os.environ.get('EMAIL_PORT', '587')))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('SENDGRID_SMTP_USERNAME', 'apikey')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_SMTP_PASSWORD', os.environ.get('SENDGRID_API_KEY', ''))
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@m.pillar.bot')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
CONTACT_FORM_TO_EMAIL = os.environ.get('CONTACT_FORM_TO_EMAIL', 'founders@trypillar.com')

# ==============================================================================
# HELP CENTER PUBLIC API CONFIGURATION (Phase 5)
# ==============================================================================
# Demo organization ID for development (used by CustomerIdMiddleware)
DEMO_ORGANIZATION_ID = os.environ.get('DEMO_ORGANIZATION_ID', '10000000-0000-0000-0000-000000000001')

# Domain suffix for subdomain resolution (e.g., {agent-slug}.trypillar.com)
HELP_CENTER_DOMAIN = os.environ.get('HELP_CENTER_DOMAIN', 'trypillar.com')

# Cloudflare for SaaS (custom domain SSL provisioning)
CLOUDFLARE_ZONE_ID = os.environ.get('CLOUDFLARE_ZONE_ID', '')
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', '')

# ==============================================================================
# FRONTEND URLs
# ==============================================================================
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
HELP_CENTER_URL = os.environ.get('HELP_CENTER_URL', 'http://localhost:3001')
BACKEND_URL = os.environ.get('HELP_CENTER_BACKEND_URL', os.environ.get('BACKEND_URL', 'http://localhost:8003'))

# Admin dashboard URL (for invitation emails, password reset, etc.)
# Defaults to dev environment — override via ADMIN_URL env var.
# dev: https://admin.pillar.bot  |  prod: https://admin.trypillar.com
ADMIN_URL = os.environ.get('ADMIN_URL', 'https://admin.trypillar.com')

# ==============================================================================
# PILLAR SDK (Backend Tool Registration)
# ==============================================================================
PILLAR_SDK_SECRET = os.environ.get('PILLAR_SDK_SECRET', '')
PILLAR_SDK_ENDPOINT_URL = os.environ.get('PILLAR_SDK_ENDPOINT_URL', '')

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
