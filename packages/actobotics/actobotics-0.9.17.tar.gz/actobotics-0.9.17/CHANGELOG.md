# Changelog

All notable changes to ACTO will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.17] - 2025-12-29

### 🚀 Streamlined Architecture & Zero External Dependencies

This release simplifies the ACTO architecture by removing the experimental Solana anchoring module. Token gating continues to work seamlessly using direct RPC calls - no additional dependencies required!

#### Removed

- **Solana Anchoring Module** (`acto/anchor/`)
  - The anchoring feature was experimental and never production-ready
  - Token gating works perfectly without the Solana Python SDK
  - Reduces package size and dependency complexity

- **`[solana]` Optional Extra**
  - No longer needed - token gating uses direct HTTP RPC calls via `httpx`
  - Simpler installation: just `pip install actobotics`

#### Changed

- **Simplified Installation**
  - Token gating works out-of-the-box with the base installation
  - No need for `pip install actobotics[solana]` anymore
  - Faster installs, smaller footprint

- **Cleaner Codebase**
  - Removed unused anchor comparison logic
  - Updated all documentation to reflect the streamlined architecture
  - Removed anchor references from API examples

#### Why This Change?

The Solana anchoring feature was added as an experimental option but was never fully implemented. Meanwhile, our token gating system works flawlessly using simple HTTP RPC calls to Solana nodes - no special SDK required. This release embraces simplicity: fewer dependencies, faster installs, and a more maintainable codebase.

**Token gating still works exactly as before!** The only change is that we removed code that was never used.

---

## [0.9.16] - 2025-12-29

### 📬 Contact Page (acto-web)

#### Added

- **New Contact Page** (`/contact`)
  - Modern, minimal design with large typography
  - Web3Forms integration for direct email sending (no mailto: popup)
  - Background image (`bg6.png`) with gradient fade effect
  - Copy-to-clipboard functionality for email address
  - Social links section (GitHub, X/Twitter, Documentation)
  - Animated success/error states with Framer Motion
  - Form validation with loading spinner

- **Footer Update**
  - Contact link added under Company section (between About and GitHub)

- **Logo Enhancement**
  - Automatic black logo detection for light background pages (Contact page)

#### Technical

- Web3Forms API key configured via environment variable
- Seamless section transitions with gradient overlays

---

## [0.9.15] - 2025-12-29

### 🎨 Website Visual Enhancements (acto-web)

This release brings significant visual improvements to the ACTO website with new animations, effects, and design refinements.

#### Added

- **Framer Motion Animations**
  - Smooth page transitions with fade, blur, and slide effects
  - Animated navigation underlines on hover
  - Spring-physics scroll progress indicator

- **Spotlight Effect on Cards**
  - Cursor-following light effect on Product cards
  - Subtle hover interactions with grayscale tones

- **"How It Works" Section Overhaul**
  - Complete redesign with dark theme and scroll-driven animations
  - Animated connecting line that grows as you scroll
  - Step icons (Bot, Database, Shield, CheckCircle) with active states
  - Progress counter showing current step (01/04)
  - Background image with dark overlay

- **Background Image Effects**
  - Use Cases section: `bg2.png` with gradient fade overlay
  - Feature Matrix (Comparison page): `bg5.png` with gradient overlay
  - Gradient overlays fade from white at top/bottom for seamless blending

- **Footer Enhancements**
  - Animated gradient border at top
  - Subtle background gradient (gray-50 → gray-100 → gray-50)

- **Scroll Progress Indicator**
  - Thin black bar at top of viewport
  - Shows page scroll progress with smooth spring animation

- **Dynamic Logo Color**
  - Logo automatically switches to white in dark sections
  - Detects Hero and "How It Works" sections

#### Changed

- **Color Palette Refinement**
  - Replaced `gray-*` colors with `neutral-*` to remove blue undertones
  - Scroll-to-Top button now uses neutral black
  - "How It Works" inactive elements use neutral grays

- **Navigation Improvements**
  - Pull-down navigation now fully hides (only "Pull me" tab visible)
  - Smooth underline animations on nav links using Framer Motion

- **Image Preloading**
  - Added `bg5.png` and `bg6.png` to preload list
  - Now preloads 10 images for faster perceived loading

#### New Components

- `SpotlightCard.tsx` - Card with cursor-following light effect
- `PageTransition.tsx` - Animated page transitions wrapper
- `AnimatedLink.tsx` - Links with smooth underline animations
- `ScrollProgress.tsx` - Page scroll progress indicator

#### Dependencies

- Added `framer-motion` for advanced animations

---

## [0.9.14] - 2025-12-27

### 🔑 API Key Groups & Reordering

This release adds group management for API keys in the dashboard, allowing you to organize keys into groups and reorder them via drag-and-drop (same functionality as Fleet devices).

#### Added

- **API Key Groups**
  - Create groups with name and description (e.g., "Production", "Development", "Testing")
  - Assign/unassign keys to groups via dropdown or drag-and-drop
  - Filter key list by group
  - Edit and delete groups
  - Group badges on key items

- **Drag-and-Drop Key Management**
  - Drag keys directly onto groups to assign them
  - Drop on "All Keys" to unassign from groups
  - Drag keys up/down to reorder within the list
  - Visual drop indicators and overlay hints
  - Order is persisted in database across sessions

- **New API Endpoints**
  - `GET /v1/keys/groups` - List all key groups
  - `POST /v1/keys/groups` - Create new group
  - `PATCH /v1/keys/groups/{id}` - Update group
  - `DELETE /v1/keys/groups/{id}` - Delete group
  - `POST /v1/keys/groups/{id}/assign` - Assign keys to group
  - `POST /v1/keys/groups/{id}/unassign` - Unassign keys from group
  - `PATCH /v1/keys/order` - Update key sort order
  - `PATCH /v1/keys/groups/order` - Update group sort order

- **Database Schema**
  - New `api_key_groups` table for group management
  - Added `group_id` and `sort_order` fields to `api_keys` table
  - Automatic schema migration for existing databases

- **Dashboard UI**
  - Key Groups section with drag-and-drop targets
  - "New Group" button in API Keys tab header
  - "Manual Order" sort option
  - Group assignment button on key items
  - Key group modal for create/edit/assign operations

---

## [0.9.13] - 2025-12-26

### 🔐 SDK Fleet Authentication Fix

This release fixes Fleet API access from the Python SDK. Previously, fleet endpoints only accepted JWT tokens (from dashboard login), now they also accept API keys.

#### Fixed

- **Fleet Endpoints Accept API Keys**
  - Fleet endpoints (`/v1/fleet/*`) now work with SDK API keys
  - Previously only JWT tokens from dashboard were accepted
  - Enables `client.fleet.get_overview()` and other fleet methods from SDK

- **Pipeline Import Error**
  - Fixed `ImportError: cannot import name 'verify_proof'` in `acto/pipeline/steps.py`
  - `verify_proof` was removed from public API but still imported by pipeline module
  - Now uses internal verification function for pipeline operations

#### Changed

- **ApiKeyStore.require()** now returns key data (including `user_id`) instead of `None`
- **New auth dependency** `require_jwt_or_api_key()` accepts either JWT or API key authentication

---

## [0.9.12] - 2025-12-26

### 🤖 Fleet Management Enhancements

This release adds drag-and-drop functionality to fleet management, device deletion, and device reordering.

#### Added

- **Drag-and-Drop Group Assignment**
  - Drag devices directly onto groups to assign them
  - Drop on "All Devices" to unassign from groups
  - Visual drop indicators and overlay hints

- **Drag-and-Drop Device Reordering**
  - Drag devices up/down to reorder within the list
  - Drop indicator shows insertion point (before/after)
  - Order is persisted in database across sessions

- **Device Deletion (Soft Delete)**
  - Delete button on device cards (trash icon)
  - Confirmation dialog with warning message
  - Soft delete preserves proof history
  - Hidden devices don't appear in fleet list

- **New API Endpoints**
  - `DELETE /v1/fleet/devices/{device_id}` - Hide/delete a device
  - `PATCH /v1/fleet/devices/order` - Update device sort order

- **Database Schema**
  - Added `sort_order` field for custom device ordering
  - Added `is_hidden` field for soft-delete functionality

- **Python SDK**
  - Added `delete_device(device_id)` method to FleetClient
  - Added `reorder_devices(device_orders)` method to FleetClient
  - New response models: `DeleteDeviceResponse`, `ReorderDevicesResponse`

#### Changed

- Device group count now calculated from actual device assignments
- Improved migration system for new columns

---

## [0.9.11] - 2025-12-26

### 👤 Account Settings & User Profile

This release introduces user profile management in the dashboard, allowing users to store optional contact and company information.

#### Added

- **Account Tab in Dashboard** - New section for managing user profile
  - Contact name field for primary contact person
  - Company/organization name
  - Email address
  - Phone number
  - Website URL
  - Location (City, Country)
  - Industry dropdown (Robotics, Manufacturing, Logistics, Healthcare, etc.)
  - Account information display (Wallet, User ID, created/login dates)

- **User Profile API Endpoints**
  - `GET /v1/profile` - Retrieve current user's profile
  - `PATCH /v1/profile` - Update profile fields (partial updates supported)

- **Database Schema Extension**
  - Extended `users` table with profile fields (all nullable/optional)
  - New fields: `contact_name`, `company_name`, `email`, `phone`, `website`, `location`, `industry`, `updated_at`

- **New Files**
  - `acto_server/static/css/account.css` - Account settings styling
  - `acto_server/static/js/account.js` - Account tab functionality

#### Technical

- Profile fields are automatically included in user responses
- PATCH endpoint only updates provided fields (null values are preserved)
- SQLite auto-migration adds new columns on startup

---

## [0.9.10] - 2025-12-23

### 🎨 Website (acto-web)

#### Added

- **SEO & Meta Tags** - Comprehensive SEO optimization with react-helmet-async
  - Dynamic meta tags (title, description, keywords) per page
  - OpenGraph tags for Facebook and LinkedIn sharing
  - Twitter Card support with large image previews
  - Canonical URLs, robots directives, and author tags
  - SEO component integrated on Home and About pages

- **Sitemap & robots.txt** - Search engine optimization
  - XML sitemap with all main pages (priority and changefreq)
  - robots.txt with crawler configuration
  - Proper indexing for Google, Bing, and other search engines

- **Scroll-to-Top Button** - Enhanced navigation UX
  - Floating button appears after 500px scroll
  - Smooth scroll animation back to top
  - Hover effects with scale and icon animation
  - Fixed position with modern styling

- **Advanced Scroll Animations** - Professional, subtle animations
  - 11 animation types: fade-up/down/left/right, scale-up/down, zoom-in, slide-left/right, flip-up, blur-in
  - Smooth cubic-bezier easing for organic motion
  - Configurable delays for staggered animations (60-360ms)
  - Intersection Observer with optimized thresholds
  - Applied across all Home and About page sections
  - 900ms duration with subtle 6px movements for professional feel

- **404 Not Found Page** - Custom error handling
  - Hero background with gradient overlay
  - Helpful navigation links (Home, Docs, GitHub)
  - Popular pages section for easy recovery
  - SEO-optimized with proper meta tags

- **Scroll Restoration** - Automatic scroll-to-top on route changes
  - Ensures users always start at top when navigating between pages
  - React Router integration with useLocation hook

#### Changed

- **Animation Refinements** - Optimized for professional appearance
  - Reduced movement distances (12px → 6px for fades)
  - Smoother easing curves for organic feel
  - Faster delays between elements (100ms → 60ms)
  - Lower trigger threshold for earlier animations
  - Duration increased to 900ms for smoother transitions

#### Components Updated

- All Home page components with scroll animations
- All About page sections with coordinated animation choreography
- Features, QuickInstall, Products, HowItWorks, UseCases, OpenSource, FleetManagement
- Navigation with mobile menu improvements

---

## [0.9.9] - 2025-12-22

### 🔧 Improvements

#### Changed

- **Rate Limiting: API Key-Based** - Rate limiting now uses API key instead of IP address
  - Fairer distribution for robots behind NAT/proxy (multiple robots sharing same IP)
  - Each API key gets its own rate limit bucket per endpoint
  - Unauthenticated endpoints (health, config) fall back to IP-based limiting
  - Supports thousands of robots without conflicts

- **Dynamic Token Configuration** - Token mint address is now loaded from server config
  - Frontend (Dashboard, Playground) fetches token config from `/v1/config/token-gating`
  - No more hardcoded token addresses in JavaScript
  - Change token via single environment variable: `ACTO_TOKEN_GATING_MINT`

- **CLI Access Check** - Now uses configured defaults
  - `--mint`, `--minimum`, and `--rpc` are now optional
  - Falls back to configured ACTO token if not specified
  - Simpler usage: `acto access check --owner WALLET_ADDRESS`

---

## [0.9.8] - 2025-12-22

### 🚀 Performance Optimization

This release includes major SQL performance improvements that eliminate memory-intensive data loading patterns.

#### Added

- **Optimized SQL Aggregation Methods** for `ProofRegistry`:
  - `count()` - Count proofs using SQL COUNT instead of len(list())
  - `count_by_robot()` - Group counts by robot_id using SQL GROUP BY
  - `count_by_task()` - Group counts by task_id using SQL GROUP BY
  - `count_by_date()` - Timeline aggregation for the last N days
  - `get_activity_range()` - First/last activity using SQL MIN/MAX
  - `exists_by_robot()` - Efficient existence check
  - `get_unique_robot_ids()` - Distinct robot IDs via SQL
  - `get_unique_task_ids()` - Distinct task IDs via SQL
  - `get_device_stats()` - Aggregated device statistics in one query

- **Optimized Fleet Store Method**:
  - `get_fleet_data_optimized()` - Uses SQL aggregations instead of loading all proofs

#### Changed

- **Wallet Stats Endpoint** (`/v1/stats/wallet/{address}`): Now uses SQL aggregations instead of loading up to 10,000 proof records into memory
- **Fleet Endpoints** (`/v1/fleet`, `/v1/fleet/devices/{id}`, `/v1/fleet/devices/{id}/name`): Now use optimized SQL queries
- **Stats Router**: Updated to use new aggregation methods

#### Performance Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Memory per request | ~10MB+ (10K records) | ~1KB (aggregates only) | **99.99%** reduction |
| Network I/O | All record data | Counts/aggregates only | **~99%** reduction |
| Query time (10K proofs) | O(n) Python iteration | O(1) SQL aggregation | **~100x** faster |

---

## [0.9.7] - 2025-12-22

### 🔧 Improvements & Bug Fixes

This release includes several stability improvements and bug fixes.

#### Fixed

- **Tests**: Updated test suite to use internal verification function (`_verify_proof_internal`) instead of deprecated `verify_proof()`
- **User-Agent Version**: SDK clients now use dynamic version from `__version__` instead of hardcoded value

#### Changed

- **Rate Limiter Memory Leak Fix**: The rate limiter now automatically cleans up stale bucket entries to prevent unbounded memory growth
  - New `bucket_ttl` setting: Bucket expiry time (default: 1 hour)
  - New `cleanup_interval` setting: Cleanup frequency (default: every 1000 requests)
  - Buckets that haven't been accessed within TTL are automatically removed

#### New Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ACTO_RATE_LIMIT_BUCKET_TTL` | `3600.0` | Time in seconds before inactive buckets expire |
| `ACTO_RATE_LIMIT_CLEANUP_INTERVAL` | `1000` | Run cleanup every N requests |

---

## [0.9.6] - 2025-12-22

### 🔒 Security Cleanup

This release removes unused legacy authentication endpoints that were never integrated into the production authentication flow.

#### Removed

- **`POST /v1/auth/token`** - Unused username/password endpoint (security risk)
- **`POST /v1/auth/refresh`** - Unused refresh token endpoint

These endpoints were placeholder code from early development and were never used by the SDK, CLI, dashboard, or any client. The actual authentication uses Solana wallet-based authentication via `/v1/auth/wallet/connect` and `/v1/auth/wallet/verify`.

#### Changed

- Updated `docs/SECURITY.md` to document the actual wallet-based authentication flow
- Added Token Gating documentation
- Cleaned up unused imports (`OAuth2TokenResponse`, `create_jwt_dependency_optional`, `require_api_key`)

#### Security

- Removed potential security vulnerability from unverified token creation endpoint
- All authentication now properly uses wallet signature verification + token gating

---

## [0.9.5] - 2025-12-21

### 🐛 SDK Client Fix

#### Fixed

- `client.get_proof()` now correctly parses API response format
- API returns `{"proof_id": ..., "envelope": ...}` - client now extracts envelope

---

## [0.9.4] - 2025-12-21

### 🐛 CI/CD Fix

#### Fixed

- Updated GitHub Actions test to not import removed `verify_proof`
- Test now validates `ACTOClient` import instead

---

## [0.9.3] - 2025-12-21

### 🐛 Server Hotfix

#### Fixed

- Server now uses internal verification function (`_verify_proof_internal`)
- SDK continues to block local verification (requires API)
- Fixed Vercel deployment crash due to missing import

---

## [0.9.2] - 2025-12-21

### 🔧 Helius RPC Integration

This release ensures all token balance checks use the backend's configured RPC (Helius) instead of public endpoints.

#### Changed

- Backend uses Helius RPC for all token balance checks when configured
- `rpc_url` is now optional in `/v1/access/check` - defaults to backend config
- SDK clients default to empty `rpc_url` (backend uses Helius)
- Removed hardcoded public RPC from dashboard and playground
- Updated all documentation to reflect Helius integration

#### Fixed

- Dashboard and playground no longer send public RPC URL
- Consistent RPC usage across all token gating checks

---

## [0.9.1] - 2025-12-21

### 🔒 API-Only Verification

This release removes local proof verification. All proofs must now be verified through the ACTO API to ensure integrity, compliance, and fleet tracking.

#### Breaking Changes

- **`verify_proof()` removed** - Local verification is no longer available
- **`verify_proof_async()` removed** - Use `AsyncACTOClient.verify()` instead
- **`ProofChain.verify_chain()`** - Now requires an `ACTOClient` parameter

#### Migration Guide

**Before (0.9.0):**
```python
from acto.proof import verify_proof
is_valid = verify_proof(envelope)  # ❌ No longer works
```

**After (0.9.1):**
```python
from acto.client import ACTOClient
client = ACTOClient(api_key="...", wallet_address="...")
result = client.verify(envelope)  # ✅ Use API verification
print(result.valid)
```

#### Changed

- `verify_proof()` now raises `ProofError` with migration instructions
- `verify_proof_async()` now raises `ProofError` with migration instructions
- `ProofChain.verify_chain(client)` now requires ACTOClient parameter
- Updated all documentation to reflect API-only verification
- Updated README.md, docs/API.md, examples/, and Jupyter notebooks
- Updated dashboard documentation

#### Why This Change?

- **Integrity**: Centralized verification ensures all proofs go through the official API
- **Compliance**: Enables audit trails and compliance reporting
- **Fleet Tracking**: Enables automatic device discovery and fleet management
- **Token Gating**: Ensures only authorized users can verify proofs

---

## [0.9.0] - 2025-12-21

### 📦 PyPI SDK & API Client

This release introduces the ACTO SDK as a standalone PyPI package and a comprehensive API client for easy integration.

#### Added

- **PyPI Publishing**
  - SDK now available via `pip install actobotics`
  - Lightweight package for end users (no server dependencies)
  - Automatic publishing via GitHub Actions on release/tag
  - Trusted Publishing with PyPI (no API tokens required)

- **API Client** (`acto.client`)
  - `ACTOClient` - Synchronous client for the ACTO API
  - `AsyncACTOClient` - Asynchronous client using httpx
  - `FleetClient` / `AsyncFleetClient` - Fleet management operations
  - Full endpoint coverage: proofs, verification, fleet, statistics
  - Automatic authentication header handling
  - Typed responses with Pydantic models
  - Custom exceptions (`ClientError`, `APIResponseError`)

- **New Client Features**
  - `client.submit_proof(envelope)` - Submit proof to registry
  - `client.verify(envelope)` - Verify proof remotely
  - `client.verify_batch(envelopes)` - Batch verification
  - `client.search_proofs(...)` - Advanced proof search
  - `client.get_wallet_stats()` - Wallet statistics
  - `client.fleet.get_overview()` - Fleet overview
  - `client.fleet.report_health(...)` - Device health reporting
  - `client.fleet.create_group(...)` - Device group management

- **Dashboard Loading Screen**
  - Elegant loading animation with ACTO logo
  - Preloads background image for smooth startup
  - Fade-in transition when ready
  - Fallback timeout (max 3 seconds)
  - No more "white flash" on page load

- **New Files**
  - `acto/client/__init__.py` - Client module exports
  - `acto/client/exceptions.py` - Custom exception classes
  - `acto/client/models.py` - Pydantic request/response models
  - `acto/client/sync_client.py` - Synchronous client implementation
  - `acto/client/async_client.py` - Async client implementation
  - `.github/workflows/publish.yml` - PyPI publishing workflow

#### Changed

- Package name on PyPI: `actobotics` (import as `acto`)
- `httpx` added to core dependencies for API client
- CLI server command now shows helpful error if server deps missing
- Conditional imports for FastAPI in security module

#### Documentation

- Updated README.md with SDK client examples
- Updated docs/API.md with Python SDK examples
- Updated dashboard docs.js with SDK code snippets
- Updated CONTRIBUTING.md with new installation method
- Updated examples/README.md and Jupyter notebooks
- Added "Installation" cells to all example notebooks

---

## [0.8.0] - 2025-12-21

### 🚀 Fleet Management System

This release introduces a comprehensive fleet management system for monitoring and organizing your robot fleet.

#### Added

- **Fleet Dashboard**
  - Device overview with proof counts, task history, and activity status
  - Device status indicators (Active, Idle, Inactive based on activity)
  - List and grid view options
  - Search and filter functionality

- **Device Details Modal**
  - Complete activity logs with timestamps
  - Task history overview
  - Health metrics visualization (when available)
  - First and last activity timestamps

- **Device Groups**
  - Create groups with name and description (e.g., "Warehouse A", "Production Line")
  - Assign/unassign devices to groups
  - Filter device list by group
  - Edit and delete groups

- **Device Customization**
  - Rename devices with custom names
  - Custom name badge indicator in device list

- **Health Monitoring**
  - CPU, Memory, Battery, Disk usage tracking
  - Network status and signal strength
  - Temperature and uptime monitoring
  - All metrics are optional (devices only report what they support)
  - Historical health data storage (30 days default)
  - Color-coded health bars (green/yellow/red)

- **Database Persistence**
  - New `fleet_devices` table for custom names and metadata
  - New `fleet_groups` table for group management
  - New `fleet_health` table for health history
  - Automatic schema migration

- **API Endpoints**
  - `GET /v1/fleet` - Fleet overview with devices and groups
  - `GET /v1/fleet/devices/{id}` - Device details with logs
  - `PATCH /v1/fleet/devices/{id}/name` - Rename device
  - `POST /v1/fleet/devices/{id}/health` - Report health metrics
  - `GET /v1/fleet/devices/{id}/health` - Get latest health
  - `GET /v1/fleet/groups` - List all groups
  - `POST /v1/fleet/groups` - Create new group
  - `PATCH /v1/fleet/groups/{id}` - Update group
  - `DELETE /v1/fleet/groups/{id}` - Delete group
  - `POST /v1/fleet/groups/{id}/assign` - Assign devices
  - `POST /v1/fleet/groups/{id}/unassign` - Remove devices

- **New Files**
  - `acto/fleet/__init__.py` - Fleet module export
  - `acto/fleet/models.py` - Database models (DeviceRecord, DeviceGroupRecord, DeviceHealthRecord)
  - `acto/fleet/store.py` - FleetStore with all database operations
  - Updated `acto_server/routers/fleet.py` - Complete API router
  - Updated `static/js/fleet.js` - Frontend module with all features
  - Updated `static/css/fleet.css` - Fleet styles and modals

- **Documentation**
  - Fleet Management section in Dashboard docs
  - Updated README.md with Fleet features
  - Complete API documentation in docs/API.md

#### Technical

- All fleet data tied to user's wallet via JWT authentication
- Health metrics history with automatic cleanup (30 days)
- Responsive design for mobile and desktop

---

## [0.7.4] - 2025-12-21

### 📊 Advanced Statistics & Analytics Dashboard

This release introduces comprehensive analytics features with interactive charts and data export capabilities.

#### Added

- **Interactive Charts (Chart.js)**
  - Activity line chart showing proof submissions over time with gradient fill
  - Request heatmap displaying API usage by hour and day of week
  - Endpoint distribution doughnut chart with color-coded segments
  - Top endpoints horizontal bar chart with HTTP method colors

- **Analytics Dashboard Components**
  - Summary cards (5 KPIs: Proofs, Verifications, Success Rate, API Requests, Active Keys)
  - Endpoint usage details table with visual usage bars
  - Responsive charts grid layout

- **Time Range Selection**
  - Quick filters: 7 days, 30 days, 90 days
  - Custom date range picker with start/end date inputs
  - Automatic chart refresh on period change

- **Data Export**
  - CSV export with summary, timeline, and endpoint data
  - JSON export with full structured data
  - Timestamped filenames for easy organization

- **New Files**
  - `static/js/charts.js` - Chart.js integration and chart creation functions
  - `static/css/analytics.css` - Analytics-specific styling (toolbar, charts, heatmap, tables)

#### Changed

- Extended `wallet-stats.js` with aggregated key statistics, advanced chart rendering, and export functions
- Updated `dashboard.html` with new analytics section and Chart.js CDN

#### Technical

- Chart.js v4.4.1 CDN for core charting functionality
- chartjs-chart-matrix plugin for heatmap visualization
- Consistent color palette across all chart types
- Loading states with spinners for async chart rendering

---

## [0.7.3] - 2025-12-21

### 🔧 Dashboard Key Management Fixes

This release fixes critical issues with API key management in the dashboard.

#### Fixed

- **Key Actions via Event Delegation** - Rename, toggle, and delete buttons now work reliably using event delegation instead of inline onclick handlers with JSON.stringify (prevents HTML attribute parsing issues)
- **Delete Keys Permanently** - Delete button now permanently removes keys from the database instead of just deactivating them
- **Toggle vs Delete Distinction** - Toggle (on/off switch) deactivates keys but keeps them visible; Delete removes them completely
- **Key Statistics Loading** - Fixed 401 errors when viewing key statistics (requires `ACTO_JWT_SECRET_KEY` environment variable on Vercel)

#### Changed

- Improved success checking for delete operations
- Keys list now loads with `include_inactive=true` to show toggled-off keys

#### Important

- **Vercel Users**: Set `ACTO_JWT_SECRET_KEY` environment variable with a fixed secret to prevent JWT validation issues across serverless instances

---

## [0.7.2] - 2025-12-21

### 🏗️ Modular Codebase Refactoring

This release focuses on code organization and maintainability by splitting the codebase into logical, reusable modules.

#### Added

- **Modular JavaScript Architecture** (`static/js/`)
  - `core.js` - Global state, API helpers, alerts, tab navigation
  - `wallet.js` - Wallet connection, multi-wallet support, authentication
  - `clipboard.js` - Copy-to-clipboard functionality
  - `modals.js` - Rename and delete confirmation dialogs
  - `keys.js` - API key CRUD, filtering, pagination, bulk actions
  - `wallet-stats.js` - Wallet statistics and activity charts
  - `playground.js` - API playground endpoint testing

- **Modular CSS Architecture** (`static/css/`)
  - `base.css` - CSS variables, reset, container, cards
  - `buttons.css` - All button variants (primary, secondary, danger, toggle, copy)
  - `forms.css` - Input fields, select, textarea styling
  - `alerts.css` - Notification alerts, status badges
  - `modals.css` - Wallet, rename, delete modal styles
  - `keys.css` - Key list, search, filter, pagination
  - `stats.css` - Statistics grid, activity charts, breakdowns
  - `playground.css` - API playground, response display
  - `fleet.css` - Fleet device management
  - `balance.css` - Insufficient balance screen
  - `responsive.css` - Mobile and tablet adaptations

- **Backend Router Modules** (`acto_server/routers/`)
  - `auth.py` - Wallet authentication, JWT endpoints
  - `keys.py` - API key management endpoints
  - `proofs.py` - Proof submission, verification, search
  - `access.py` - Token gating, access control
  - `stats.py` - Wallet statistics endpoints
  - `fleet.py` - Fleet management endpoints

#### Changed

- Dashboard now loads modular JS/CSS instead of monolithic files
- Better separation of concerns for easier maintenance
- Improved code reusability across modules
- Smaller file sizes for faster development iteration

#### Benefits

- ✅ Better maintainability - each module has clear responsibility
- ✅ Easier development - changes in one area don't affect others
- ✅ Reusability - modules can be imported individually
- ✅ Readability - smaller files are easier to understand
- ✅ Team collaboration - fewer merge conflicts

---

## [0.7.1] - 2025-12-21

### 🔧 Fleet Improvements

#### Changed
- Fleet data now uses JWT authentication (wallet-based) instead of API key
- Moved fleet code to separate `fleet.js` module for better code organization
- New `/v1/fleet` endpoint that returns fleet data tied to wallet session

#### Fixed
- Fleet tab now correctly loads devices without requiring an API key

---

## [0.7.0] - 2025-12-21

### 🚀 Fleet Management & Helius RPC Integration

#### Added

- **Fleet Tab**: New dashboard section to monitor your robot fleet
  - Overview statistics (active devices, total devices, proofs, tasks)
  - Device list with individual stats
  - Online/offline status indicators
  - Last activity timestamps
- **Helius RPC Support**: Better rate limits for Solana token balance checks
  - Set `ACTO_HELIUS_API_KEY` for automatic Helius integration
  - Falls back to public RPC if not configured
- **Site Logo**: Added ACTO logo to dashboard header

#### Changed

- Token balance check now happens at wallet connection (not just API calls)
- Insufficient balance shows dedicated screen with clear messaging
- Improved RPC configuration flexibility

#### Fixed

- Fixed token mint address consistency across configuration files
- Fixed Pydantic settings property issue for RPC URL

---

## [0.6.0] - 2025-12-20

### 🎉 Major Release: Dashboard 2.0 & Multi-Wallet Support

This release brings a completely revamped dashboard experience with multi-wallet support, an interactive API playground, and comprehensive wallet statistics.

### Added

#### Dashboard Features
- **Multi-Wallet Support**: Connect with Phantom, Solflare, Backpack, Glow, or Coinbase Wallet
- **API Playground**: Test API endpoints directly in your browser with live responses
- **Wallet Statistics Dashboard**: 
  - Proofs submitted counter
  - Total verifications with success rate
  - Activity timeline (last 30 days)
  - Breakdown by robot and task type
- **API Key Management**: Create, view, and delete API keys with usage statistics
- **Session Persistence**: Auto-reconnect wallet on page reload

#### API Endpoints
- `POST /v1/proofs/search` - Search and filter proofs with pagination
  - Filter by task_id, robot_id, run_id, signer_public_key
  - Date range filtering (created_after, created_before)
  - Full-text search across metadata
  - Configurable sorting and pagination
- `POST /v1/verify/batch` - Batch verify multiple proofs in a single request
  - Reduces network latency for bulk operations
  - Returns individual results with summary statistics
- `GET /v1/stats/wallet/{address}` - Get comprehensive wallet statistics
  - Proof submission counts
  - Verification statistics with success rates
  - Activity timeline
  - Breakdown by robot and task

### Changed
- Improved error handling with user-friendly messages
- Better session management with JWT token persistence
- Updated documentation with new endpoint examples

### Fixed
- Fixed infinite loop in documentation JS module
- Fixed race condition causing spurious authentication errors
- Fixed API key not being removed from localStorage when deleted
- Fixed verification statistics not counting correctly (endpoint key mismatch)
- Fixed auto-logout issue when switching dashboard tabs

---

## [0.5.23] - 2025-12-19

### Added
- Proof Search & Filter API endpoint
- Batch Verification API endpoint
- Wallet Statistics API endpoint

---

## [0.5.22] - 2025-12-18

### Added
- Initial dashboard with wallet connection
- API key creation and management
- Basic proof submission and verification

---

## [0.4.0] - 2025-12-01

### Added
- OAuth2/JWT authentication support
- Role-Based Access Control (RBAC)
- Audit logging with multiple backends
- Encryption at rest (AES-128)
- TLS/SSL support
- Secrets management (Vault, AWS)
- PII detection and masking
- Signing key rotation

---

## [0.3.0] - 2025-11-15

### Added
- Interactive CLI mode
- Shell completion (bash, zsh, fish, PowerShell)
- Configuration file support
- Async/await operations
- Context managers for registry
- Jupyter notebook examples

---

## [0.2.0] - 2025-11-01

### Added
- Token gating module (Solana SPL)
- Pipeline system
- API key authentication
- Rate limiting middleware
- Reputation scoring
- Prometheus metrics

---

## [0.1.0] - 2025-10-15

### Added
- Initial release
- Proof creation and verification
- SQLite registry
- FastAPI server
- CLI tools

