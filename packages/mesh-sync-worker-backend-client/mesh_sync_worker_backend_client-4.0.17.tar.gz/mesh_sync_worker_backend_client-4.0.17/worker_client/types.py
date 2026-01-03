"""Auto-generated message types"""

from typing import TypedDict, Optional, List, Dict

# Message type constants
class MessageTypes:
    """Message type constants for type-safe queue operations"""
    BACKEND_LOGGING_EVENT = 'backend-logging-event'
    EKG_EDGE_BATCH_CREATE_COMPLETED = 'ekg-edge-batch-create-completed'
    EKG_EDGE_BATCH_CREATE_REQUEST = 'ekg-edge-batch-create-request'
    ETSY_ANALYTICS_SYNC_COMPLETED = 'etsy-analytics-sync-completed'
    ETSY_ANALYTICS_SYNC_REQUEST = 'etsy-analytics-sync-request'
    ETSY_PUBLISH_LISTING_COMPLETED = 'etsy-publish-listing-completed'
    ETSY_PUBLISH_LISTING_REQUEST = 'etsy-publish-listing-request'
    FILE_DOWNLOAD_COMPLETED = 'file-download-completed'
    FILE_DOWNLOAD_REQUEST = 'file-download-request'
    FILE_VECTORIZE_COMPLETED = 'file-vectorize-completed'
    FILE_VECTORIZE_REQUEST = 'file-vectorize-request'
    MARKETPLACE_ANALYTICS_SYNC_COMPLETED = 'marketplace-analytics-sync-completed'
    MARKETPLACE_ANALYTICS_SYNC_REQUEST = 'marketplace-analytics-sync-request'
    MARKETPLACE_CONNECTION_SYNC_COMPLETED = 'marketplace-connection-sync-completed'
    MARKETPLACE_CONNECTION_SYNC_REQUEST = 'marketplace-connection-sync-request'
    MARKETPLACE_CREDENTIAL_ROTATION_COMPLETED = 'marketplace-credential-rotation-completed'
    MARKETPLACE_CREDENTIAL_ROTATION_REQUEST = 'marketplace-credential-rotation-request'
    MARKETPLACE_LISTING_DESCRIPTION_GENERATION_COMPLETED = 'marketplace-listing-description-generation-completed'
    MARKETPLACE_LISTING_DESCRIPTION_GENERATION_REQUEST = 'marketplace-listing-description-generation-request'
    MARKETPLACE_LISTING_SYNC_COMPLETED = 'marketplace-listing-sync-completed'
    MARKETPLACE_LISTING_SYNC_REQUEST = 'marketplace-listing-sync-request'
    MARKETPLACE_LISTING_TAGS_GENERATION_COMPLETED = 'marketplace-listing-tags-generation-completed'
    MARKETPLACE_LISTING_TAGS_GENERATION_REQUEST = 'marketplace-listing-tags-generation-request'
    MARKETPLACE_LISTING_TITLE_GENERATION_COMPLETED = 'marketplace-listing-title-generation-completed'
    MARKETPLACE_LISTING_TITLE_GENERATION_REQUEST = 'marketplace-listing-title-generation-request'
    MARKETPLACE_PUBLISH_LISTING_COMPLETED = 'marketplace-publish-listing-completed'
    MARKETPLACE_PUBLISH_LISTING_REQUEST = 'marketplace-publish-listing-request'
    MEDIA_BATCH_DOWNLOAD_COMPLETED = 'media-batch-download-completed'
    MEDIA_BATCH_DOWNLOAD_REQUEST = 'media-batch-download-request'
    METAMODEL_METADATA_GENERATION_COMPLETED = 'metamodel-metadata-generation-completed'
    METAMODEL_METADATA_GENERATION_REQUEST = 'metamodel-metadata-generation-request'
    MODEL_ANALYTICS_COLLECTION_REQUEST = 'model-analytics-collection-request'
    MODEL_DISCOVERY_FOLDER_PROCESSED_EVENT = 'model-discovery-folder-processed-event'
    MODEL_DISCOVERY_SCAN_FOUND_EVENT = 'model-discovery-scan-found-event'
    MODEL_DISCOVERY_SCAN_PROGRESS_EVENT = 'model-discovery-scan-progress-event'
    MODEL_DISCOVERY_SCAN_REQUEST = 'model-discovery-scan-request'
    MODEL_FINDER_INDEX_REQUEST = 'model-finder-index-request'
    MODEL_FINDER_RESPONSE = 'model-finder-response'
    MODEL_FINDER_SEARCH_REQUEST = 'model-finder-search-request'
    MODEL_METADATA_GENERATION_COMPLETED = 'model-metadata-generation-completed'
    MODEL_METADATA_GENERATION_REQUEST = 'model-metadata-generation-request'
    MODEL_METAMODEL_DETECTION_FOUND = 'model-metamodel-detection-found'
    MODEL_METAMODEL_DETECTION_REQUEST = 'model-metamodel-detection-request'
    MODEL_SELLABILITY_ANALYSIS_COMPLETED = 'model-sellability-analysis-completed'
    MODEL_SELLABILITY_ANALYSIS_REQUEST = 'model-sellability-analysis-request'
    MODEL_SEMANTIC_ANALYSIS_COMPLETED = 'model-semantic-analysis-completed'
    MODEL_SEMANTIC_ANALYSIS_REQUEST = 'model-semantic-analysis-request'
    MODEL_TECHNICAL_METADATA_COMPLETED = 'model-technical-metadata-completed'
    MODEL_TECHNICAL_METADATA_REQUEST = 'model-technical-metadata-request'
    THUMBNAIL_GENERATION_COMPLETED = 'thumbnail-generation-completed'
    THUMBNAIL_GENERATION_REQUEST = 'thumbnail-generation-request'
    USER_ENGAGEMENT_EVENT = 'user-engagement-event'
    WORKER_ANALYTICS_EVENT = 'worker-analytics-event'
    WORKER_METRICS_ENRICHED_EVENT = 'worker-metrics-enriched-event'



class BackendLoggingEventMessage(TypedDict, total=False):
    """Centralized logging event for capturing all warn/error/failure logs from meshsync-backend.
This event is sent to ELK for centralized monitoring, alerting, and debugging.

Automatically emitted by the custom Pino logger interceptor when:
- logger.warn() is called
- logger.error() is called
- uncaught exceptions occur
- request failures happen (4xx, 5xx responses)

Used for:
- System health monitoring
- Error tracking and alerting
- Performance degradation detection
- Security incident tracking
- Compliance and audit trails
"""
    eventType: str  # Type of logging event
    timestamp: str  # ISO 8601 timestamp when the log was generated
    level: str  # Log level severity
    message: str  # Human-readable log message
    context: str  # Logger context (typically the class/service name)
    requestId: str  # Unique request ID for correlation (X-Request-Id header) (optional)
    userId: str  # ID of the authenticated user (if available) (optional)
    httpMethod: str  # HTTP method of the request (optional)
    httpUrl: str  # Request URL path (without query params for privacy) (optional)
    httpStatusCode: object  # HTTP response status code (optional)
    errorType: str  # Error class/type name (optional)
    errorStack: str  # Stack trace (sanitized, no sensitive data) (optional)
    errorCode: str  # Application-specific error code for categorization (optional)
    metadata: Dict[str, object]  # Additional structured context (sanitized, no PII) (optional)
    environment: str  # Deployment environment (optional)
    serviceVersion: str  # Backend service version (optional)
    hostname: str  # Server hostname/pod name (optional)
    durationMs: float  # Operation duration in milliseconds (if applicable) (optional)

class EkgEdgeBatchCreateCompletedMessage(TypedDict, total=False):
    """Completion event for EKG edge batch creation with propagation results."""
    requestId: str  # Original request ID from ekg-edge-batch-create-request
    success: bool  # Whether the batch operation succeeded
    statistics: Dict[str, object]  # Batch operation statistics
    conflicts: List[Dict[str, object]]  # List of high-conflict edges requiring review (optional)
    errors: List[Dict[str, object]]  # Errors encountered during processing (optional)
    graphMetrics: Dict[str, object]  # Overall graph state after this batch (optional)

class EkgEdgeBatchCreateRequestMessage(TypedDict, total=False):
    """Create multiple EKG edges with Dempster-Shafer mass functions. Triggered by metamodel detection completion."""
    requestId: str  # Unique request ID for tracking (e.g., metamodel detection job ID)
    source: str  # Source of the edges: metamodel-heuristic, manual, taxonomy-import, etc.
    edges: List[Dict[str, object]]  # Batch of edges to create/update in the EKG
    propagationOptions: Dict[str, object]  # Options for evidential edge propagation after edge creation (optional)
    webhookUrl: str  # Optional webhook URL for async completion notification (optional)

class EtsyAnalyticsSyncCompletedMessage(TypedDict, total=False):
    """Contains synced analytics data for Etsy listings. Backend stores this in etsy_analytics_snapshots table and indexes to ELK.
"""
    originalJobId: str  #  (optional)
    status: str  #  (optional)
    syncedCount: object  # Number of listings successfully synced (optional)
    errorCount: object  # Number of listings that failed (optional)
    results: List[Dict[str, object]]  # Analytics for each synced listing (optional)
    credentialUpdate: Dict[str, object]  # New credentials if token was refreshed during operation (optional)
    errors: List[Dict[str, object]]  # Errors for failed listings (optional)
    syncedAt: str  #  (optional)
    nextScheduledSync: str  # When next automatic sync should occur (optional)

class EtsyAnalyticsSyncRequestMessage(TypedDict, total=False):
    """Syncs analytics data from Etsy API for one or more listings. Fetches views, favorites, sales, revenue, and traffic source data.
Can sync: - Specific listings (provide listingIds) - All user listings (provide userId, empty listingIds) - Shop-level analytics (provide shopId)
"""
    listingIds: List[Dict[str, object]]  # Internal listing IDs to sync. Empty = sync all for user. (optional)
    userId: str  # User whose listings to sync (if listingIds empty) (optional)
    shopId: str  # Etsy shop ID for shop-level analytics (optional)
    credentials: Dict[str, object]  # Etsy OAuth credentials (optional)
    timeRange: Dict[str, object]  # Date range for historical analytics (optional)
    syncOptions: Dict[str, object]  #  (optional)
    etsyCredentials: Dict[str, object]  # Encrypted Etsy OAuth credentials (optional)
    webhookUrl: str  #  (optional)

class EtsyPublishListingCompletedMessage(TypedDict, total=False):
    """Indicates completion of Etsy listing publication. Contains external Etsy listing ID and URL, or error details if failed.
"""
    originalJobId: str  # BullMQ job ID from request (optional)
    listingId: str  # Internal marketplace_items ID (optional)
    metamodelId: str  # Metamodel that was published (optional)
    materialName: str  # Material variant name (optional)
    status: str  # Publication result (optional)
    etsyListingId: str  # External Etsy listing ID (only if status=SUCCESS) (optional)
    etsyListingUrl: str  # URL to view listing on Etsy (only if status=SUCCESS) (optional)
    credentialUpdate: Dict[str, object]  # New credentials if token was refreshed during operation (optional)
    etsyFileId: str  # Etsy digital file ID (only if status=SUCCESS) (optional)
    error: Dict[str, object]  # Error details (only if status=FAILED) (optional)
    publishedAt: str  # When the listing was created (only if status=SUCCESS) (optional)
    processingDuration: object  # Processing time in milliseconds (optional)

class EtsyPublishListingRequestMessage(TypedDict, total=False):
    """Publishes a single metamodel listing to Etsy for a specific material variant. Creates Etsy listing, uploads digital file, and returns external listing ID.
This message is enqueued for EACH material variant when publishing a metamodel.
Example: Publishing a metamodel with PLA, Resin, ABS materials creates 3 jobs.
"""
    listingId: str  # Internal marketplace_items table ID (optional)
    metamodelId: str  # Metamodel being published (optional)
    ownerId: str  # User ID who owns the metamodel (optional)
    credentials: Dict[str, object]  # Etsy OAuth credentials (optional)
    materialVariant: Dict[str, object]  # Material-specific listing configuration (optional)
    baseListingData: Dict[str, object]  # Common listing information (optional)
    publishOptions: Dict[str, object]  #  (optional)
    etsyCredentials: Dict[str, object]  # Encrypted Etsy OAuth credentials (optional)
    fileMetadata: Dict[str, object]  # Digital file to upload (optional)
    webhookUrl: str  # Callback URL for completion notification (optional)

class FileDownloadCompletedMessage(TypedDict, total=False):
    """Notifies that a file download has been processed, indicating success or failure."""
    originalJobId: str  # The ID of the initial 'file-download-request' job this event corresponds to. (optional)
    modelId: str  # The unique identifier for the downloaded model. (optional)
    status: str  # The final status of the download operation. (optional)
    s3Location: Dict[str, object]  # Details of the file's location in Minio S3 (present on success). (optional)
    errorMessage: str  # Contains error details if the status is FAILED. (optional)
    downloadedAt: str  # The timestamp when the download was completed or failed. (optional)

class FileDownloadRequestMessage(TypedDict, total=False):
    """Downloads model file from storage provider to MinIO for processing pipeline. 
Acts as parent job for thumbnail generation, technical metadata analysis, and metadata generation.

Retry Configuration:
- Automatic retry enabled for transient failures (connection errors, timeouts)
- Default: 5 attempts with exponential backoff (2s, 4s, 8s, 16s, 32s)
- Retry on: STORAGE_TIMEOUT, NETWORK_ERROR, MINIO_UNAVAILABLE, CONNECTION_REFUSED
- No retry on: INVALID_CREDENTIALS, FILE_NOT_FOUND, PERMISSION_DENIED
"""
    modelId: str  # The unique identifier for the model to be downloaded. (optional)
    ownerId: str  # The identifier of the user who owns the model. Optional - if not provided, will be retrieved from StorageConnection. (optional)
    storageLocation: Dict[str, object]  # The storage location of the model. (optional)
    metadata: Dict[str, object]  # Optional metadata from discovery. For Thingiverse, contains downloadUrl for direct file access. (optional)
    credentials: Dict[str, object]  # Decrypted credentials required for this specific download operation. Injected by the backend. (optional)
    minioDestination: Dict[str, object]  # Destination in MinIO where file will be uploaded after download. (optional)
    autoEnqueueChildren: bool  # Automatically enqueue thumbnail generation, technical metadata analysis, and metadata generation jobs after download completes. (optional)
    previewType: str  # Preview type for thumbnail generation (passed to child job). (optional)
    generate360Views: bool  # Generate 16 angle views for 360° preview (passed to child job). (optional)
    webhookUrl: str  # Optional webhook URL to call when download completes. If provided, worker will POST completion status to this endpoint. (optional)

class FileVectorizeCompletedMessage(TypedDict, total=False):
    """Result of the vectorization process containing the embedding vector."""
    fileId: str  #  (optional)
    vector: List[Dict[str, object]]  # The computed embedding vector (optional)
    modelName: str  #  (optional)
    dimension: object  # Length of the vector (e.g., 512) (optional)

class FileVectorizeRequestMessage(TypedDict, total=False):
    """Request to generate a vector embedding for an image file using CLIP."""
    fileId: str  # The ID of the file in the database (optional)
    storageItem: object  # Location of the image file (optional)
    modelName: str  # Optional: Specific model version to use (optional)

class MarketplaceAnalyticsSyncCompletedMessage(TypedDict, total=False):
    """Contains synced analytics data for marketplace listings. Backend stores this in marketplace_analytics_snapshots table and indexes to ELK. Works with any marketplace provider."""
    originalJobId: str  # BullMQ job ID from original request (optional)
    marketplaceProvider: str  # Marketplace provider type (etsy, ebay, etc.) (optional)
    status: str  # Sync result (SUCCESS, PARTIAL_SUCCESS, or FAILED) (optional)
    syncedCount: object  # Number of listings successfully synced (optional)
    errorCount: object  # Number of listings that failed (optional)
    results: List[Dict[str, object]]  # Analytics for each synced listing (optional)
    errors: List[Dict[str, object]]  # Errors for failed listings (optional)
    syncedAt: str  # When sync completed (ISO 8601) (optional)
    nextScheduledSync: str  # When next automatic sync should occur (ISO 8601) (optional)

class MarketplaceAnalyticsSyncRequestMessage(TypedDict, total=False):
    """Syncs analytics data from marketplace API for one or more listings. Fetches views, favorites, sales, revenue, and traffic source data. Can sync: specific listings, all user listings, or shop-level analytics. Works with any marketplace provider that supports analytics (etsy, ebay, etc.)."""
    marketplaceProvider: str  # Marketplace provider type (etsy, ebay, etc.) (optional)
    marketplaceConnectionId: str  # UUID of the marketplace connection configuration (optional)
    listingIds: List[Dict[str, object]]  # Internal listing UUIDs to sync. Empty array = sync all for user. (optional)
    userId: str  # UUID of user whose listings to sync (if listingIds empty) (optional)
    externalShopId: str  # External marketplace shop ID for shop-level analytics (optional)
    timeRange: Dict[str, object]  # Date range for historical analytics (optional)
    syncOptions: Dict[str, object]  # Optional sync configuration (optional)
    marketplaceCredentials: Dict[str, object]  # Encrypted marketplace credentials (retrieved from marketplaceConnectionId) (optional)
    webhookUrl: str  # Callback URL for completion notification (optional)

class MarketplaceConnectionSyncCompletedMessage(TypedDict, total=False):
    """Notification that marketplace connection sync has completed. Contains updated connection metadata, profile information, and sync statistics.
"""
    requestId: str  # Original request ID for correlation (optional)
    connectionId: str  # Marketplace connection that was synced (optional)
    marketplaceId: str  # Marketplace provider ID (optional)
    userId: str  # Connection owner user ID (optional)
    status: str  # Overall sync result status (optional)
    syncType: str  # Type of sync that was performed (optional)
    connectionData: Dict[str, object]  # Updated connection information (optional)
    categories: List[Dict[str, object]]  # Available marketplace categories (optional)
    statistics: Dict[str, object]  # Sync operation statistics (optional)
    completedAt: str  # When sync completed (optional)
    error: Dict[str, object]  # Error details if sync failed (optional)

class MarketplaceConnectionSyncRequestMessage(TypedDict, total=False):
    """Requests synchronization of marketplace connection data including: - Profile information and shop details - Account status and permissions - Available categories and shipping profiles - Rate limits and API quotas
This is typically triggered after initial connection or periodically to keep marketplace metadata up to date.
"""
    connectionId: str  # Internal marketplace connection ID (optional)
    marketplaceId: str  # Marketplace provider ID (etsy, ebay, etc.) (optional)
    userId: str  # User who owns this connection (optional)
    syncType: str  # Type of sync to perform (optional)
    priority: str  # Processing priority (optional)
    requestId: str  # Unique request identifier for tracking (optional)
    webhookUrl: str  # Webhook URL to call when sync completes (optional)
    metadata: Dict[str, object]  # Additional context data (optional)

class MarketplaceCredentialRotationCompletedMessage(TypedDict, total=False):
    """Notification that marketplace credential rotation has completed. Contains the rotation results, new credential metadata, and any issues encountered.
"""
    requestId: str  # Original rotation request ID (optional)
    connectionId: str  # Marketplace connection that was rotated (optional)
    marketplaceId: str  # Marketplace provider ID (optional)
    userId: str  # Connection owner user ID (optional)
    status: str  # Overall rotation operation status (optional)
    rotationType: str  # Type of rotation that was performed (optional)
    reason: str  # Original reason for rotation (optional)
    newCredentials: Dict[str, object]  # Metadata about new credentials (optional)
    oldCredentials: Dict[str, object]  # Status of previous credentials (optional)
    operationDetails: Dict[str, object]  # Details of the rotation operation (optional)
    connectionStatus: Dict[str, object]  # Connection status after credential rotation (optional)
    nextRotation: Dict[str, object]  # Information about next scheduled rotation (optional)
    error: Dict[str, object]  # Error details if rotation failed (optional)
    notifications: List[Dict[str, object]]  # Notifications sent as part of rotation (optional)

class MarketplaceCredentialRotationRequestMessage(TypedDict, total=False):
    """Requests rotation/refresh of marketplace connection credentials. This is used for: - OAuth token refresh when tokens are near expiry - API key rotation for enhanced security - Re-authentication after connection errors - Scheduled credential updates
"""
    connectionId: str  # Marketplace connection ID requiring credential rotation (optional)
    marketplaceId: str  # Marketplace provider ID (etsy, ebay, etc.) (optional)
    userId: str  # User who owns the connection (optional)
    rotationType: str  # Type of credential rotation to perform (optional)
    reason: str  # Reason for credential rotation (optional)
    urgency: str  # How urgently the rotation is needed (optional)
    currentCredentials: Dict[str, object]  # Current credential metadata (no actual secrets) (optional)
    options: Dict[str, object]  # Rotation configuration options (optional)
    requestId: str  # Unique request identifier (optional)
    webhookUrl: str  # Webhook URL for completion notification (optional)
    scheduledAt: str  # When this rotation was scheduled (if scheduled) (optional)
    metadata: Dict[str, object]  # Additional request context (optional)

class MarketplaceListingDescriptionGenerationCompletedMessage(TypedDict, total=False):
    """Notifies backend that marketplace description generation completed. Contains generated description with metadata tracking (AI model, confidence, generation timestamp)."""
    modelId: str  # UUID of the model that was processed
    entityType: str  # Type of entity processed
    description: str  # SEO-optimized marketplace description (3-5 sentences)
    metadata: Dict[str, object]  # Content generation metadata for tracking
    error: str  # Error message if generation failed (optional)

class MarketplaceListingDescriptionGenerationRequestMessage(TypedDict, total=False):
    """Generates SEO-optimized marketplace description for a 3D model using LLM vision analysis. Worker receives model data, technical metadata, and thumbnail URLs to generate compelling product descriptions tailored to the target marketplace."""
    modelId: str  # UUID of the model (reference only)
    entityType: str  # Type of entity being processed
    entityName: str  # Name/title of the model or metamodel
    targetMarketplace: str  # Target marketplace ID (e.g., 'etsy', 'ebay', 'thingiverse')
    userId: str  # UUID of the user requesting generation
    webhookUrl: str  # Callback URL for completion notification (optional)
    technicalMetadata: Dict[str, object]  # Technical analysis data for context (optional)
    thumbnailUrls: List[Dict[str, object]]  # URLs to 360-degree thumbnail views (optional)
    existingTags: List[Dict[str, object]]  # Currently assigned tags for context (optional)
    existingCategory: str  # Current classification for context (optional)

class MarketplaceListingSyncCompletedMessage(TypedDict, total=False):
    """Notification that marketplace listing sync operation has completed. Contains detailed results of the sync including created/updated listings, errors encountered, and performance statistics.
"""
    requestId: str  # Original request ID for correlation (optional)
    connectionId: str  # Marketplace connection that was synced (optional)
    marketplaceId: str  # Marketplace provider ID (optional)
    userId: str  # Connection owner user ID (optional)
    status: str  # Overall sync operation status (optional)
    syncDirection: str  # Direction of sync that was performed (optional)
    statistics: Dict[str, object]  # Detailed sync operation statistics (optional)
    results: Dict[str, object]  # Detailed sync results by operation (optional)
    successfulListings: List[Dict[str, object]]  # Details of successfully processed listings (optional)
    failedListings: List[Dict[str, object]]  # Details of listings that failed to sync (optional)
    errors: List[Dict[str, object]]  # Non-listing-specific errors encountered (optional)
    completedAt: str  # When sync operation completed (optional)
    nextSyncRecommendedAt: str  # When next sync is recommended (optional)

class MarketplaceListingSyncRequestMessage(TypedDict, total=False):
    """Requests synchronization of marketplace listings for a connection. Can sync specific listings or all listings for a marketplace connection.
Includes bidirectional sync: - Pull: Fetch listings from marketplace to update local database - Push: Update marketplace listings with local changes - Full: Both pull and push operations
"""
    connectionId: str  # Marketplace connection ID (optional)
    marketplaceId: str  # Marketplace provider ID (etsy, ebay, etc.) (optional)
    userId: str  # User who owns the connection (optional)
    syncDirection: str  # Direction of sync operation (optional)
    syncScope: str  # Scope of listings to sync (optional)
    listingIds: List[Dict[str, object]]  # Specific listing IDs to sync (if syncScope=specific) (optional)
    externalListingIds: List[Dict[str, object]]  # External marketplace listing IDs to sync (optional)
    options: Dict[str, object]  # Sync configuration options (optional)
    priority: str  # Processing priority (optional)
    requestId: str  # Unique request identifier (optional)
    webhookUrl: str  # Webhook URL for completion notification (optional)
    metadata: Dict[str, object]  # Additional request context (optional)

class MarketplaceListingTagsGenerationCompletedMessage(TypedDict, total=False):
    """Notifies backend that marketplace tags generation completed. Contains generated tags optimized for discoverability with metadata tracking."""
    modelId: str  # UUID of the model that was processed
    entityType: str  # Type of entity processed
    tags: List[Dict[str, object]]  # Generated searchability tags (style, technical, usage keywords)
    metadata: Dict[str, object]  # Content generation metadata for tracking
    error: str  # Error message if generation failed (optional)

class MarketplaceListingTagsGenerationRequestMessage(TypedDict, total=False):
    """Generates searchability tags for a 3D model optimized for marketplace discoverability. Worker creates style, technical, and usage keywords following marketplace tag limits and SEO best practices."""
    modelId: str  # UUID of the model (reference only)
    entityType: str  # Type of entity being processed
    entityName: str  # Name/title of the model or metamodel
    targetMarketplace: str  # Target marketplace ID (e.g., 'etsy', 'ebay', 'thingiverse')
    userId: str  # UUID of the user requesting generation
    webhookUrl: str  # Callback URL for completion notification (optional)
    technicalMetadata: Dict[str, object]  # Technical analysis data for tag generation (optional)
    thumbnailUrls: List[Dict[str, object]]  # URLs to 360-degree thumbnail views for visual analysis (optional)
    existingTags: List[Dict[str, object]]  # Currently assigned tags to supplement or replace (optional)
    existingCategory: str  # Current classification for category-based tags (optional)
    tagLimit: float  # Maximum number of tags for marketplace (e.g., 13 for Etsy) (optional)

class MarketplaceListingTitleGenerationCompletedMessage(TypedDict, total=False):
    """Notifies backend that marketplace title generation completed. Contains generated title with metadata tracking."""
    modelId: str  # UUID of the model that was processed
    entityType: str  # Type of entity processed
    title: str  # Marketplace-optimized title
    metadata: Dict[str, object]  # Content generation metadata for tracking
    error: str  # Error message if generation failed (optional)

class MarketplaceListingTitleGenerationRequestMessage(TypedDict, total=False):
    """Generates marketplace-optimized title for a 3D model. Worker creates concise, SEO-friendly titles following marketplace character limits and best practices."""
    modelId: str  # UUID of the model (reference only)
    entityType: str  # Type of entity being processed
    currentName: str  # Current model/metamodel name
    targetMarketplace: str  # Target marketplace ID (e.g., 'etsy', 'ebay', 'thingiverse')
    userId: str  # UUID of the user requesting generation
    webhookUrl: str  # Callback URL for completion notification (optional)
    technicalMetadata: Dict[str, object]  # Technical analysis data for context (optional)
    existingTags: List[Dict[str, object]]  # Currently assigned tags for SEO keywords (optional)
    existingCategory: str  # Current classification for categorization (optional)
    characterLimit: float  # Maximum character count for marketplace (e.g., 140 for Etsy) (optional)

class MarketplacePublishListingCompletedMessage(TypedDict, total=False):
    """Indicates completion of marketplace listing publication. Contains external listing ID and URL, or error details if failed. Works with any marketplace provider (etsy, ebay, etc.)."""
    originalJobId: str  # BullMQ job ID from original request (optional)
    listingId: str  # Internal marketplace_items UUID (optional)
    metamodelId: str  # UUID of the metamodel that was published (optional)
    marketplaceProvider: str  # Marketplace provider type (etsy, ebay, etc.) (optional)
    materialName: str  # Material variant name (optional)
    status: str  # Publication result (SUCCESS or FAILED) (optional)
    externalListingId: str  # External marketplace listing ID (only if status=SUCCESS) (optional)
    externalListingUrl: str  # URL to view listing on marketplace (only if status=SUCCESS) (optional)
    externalFileId: str  # External marketplace file ID (only if status=SUCCESS) (optional)
    error: Dict[str, object]  # Error details (only if status=FAILED) (optional)
    publishedAt: str  # When the listing was created (ISO 8601, only if status=SUCCESS) (optional)
    processingDuration: object  # Processing time in milliseconds (optional)

class MarketplacePublishListingRequestMessage(TypedDict, total=False):
    """Publishes a single metamodel listing to a marketplace for a specific material variant. Creates listing, uploads digital file, and returns external listing ID. This message is enqueued for EACH material variant when publishing a metamodel. The marketplace type (etsy, ebay, etc.) is determined by the marketplaceProvider field."""
    listingId: str  # Internal marketplace_items table UUID (optional)
    metamodelId: str  # UUID of the metamodel being published (optional)
    ownerId: str  # UUID of the user who owns the metamodel (optional)
    marketplaceProvider: str  # Marketplace provider type (etsy, ebay, leboncoin, etc.) (optional)
    marketplaceConnectionId: str  # UUID of the marketplace connection configuration (optional)
    materialVariant: Dict[str, object]  # Material-specific listing configuration (optional)
    baseListingData: Dict[str, object]  # Common listing information shared across variants (optional)
    publishOptions: Dict[str, object]  # Publishing configuration (marketplace-specific options) (optional)
    marketplaceCredentials: Dict[str, object]  # Encrypted marketplace credentials (retrieved from marketplaceConnectionId) (optional)
    fileMetadata: Dict[str, object]  # Digital file to upload (optional)
    webhookUrl: str  # Callback URL for completion notification (optional)

class MediaBatchDownloadCompletedMessage(TypedDict, total=False):
    """Notifies that a batch media download has been completed."""
    batchId: str  # The unique identifier for the batch download operation.
    status: str  # The final status of the batch download operation.
    processedFiles: List[Dict[str, object]]  # List of successfully processed files. (optional)
    failedFiles: List[Dict[str, object]]  # List of files that failed to process. (optional)
    processedAt: str  # Timestamp when the batch processing completed.
    statistics: Dict[str, object]  # Statistics about the batch processing. (optional)

class MediaBatchDownloadRequestMessage(TypedDict, total=False):
    """Request to download and process a batch of media files from a storage provider. Images are compressed and resized to specified dimensions, converted to WebP format. Text files and documents are processed and stored with metadata. All processed files are uploaded to MinIO S3 storage under the media/{batchId}/ prefix.
"""
    batchId: str  # Unique identifier for this batch of media files. Used for organizing processed files in S3 storage (media/{batchId}/) and correlating with completion responses. (optional)
    downloadStrategy: str  # Download strategy for media files: - storage_provider: Download from authenticated storage connection (Google Drive, SFTP, etc.) - external_url: Download from public HTTP URLs (CDN, API responses, Thingiverse, etc.) (optional)
    entityType: str  # Type of entity these media files belong to. Used for linking downloaded media to the correct entity in the database. (optional)
    entityId: str  # UUID of the model or metamodel entity that owns these media files. Used for creating storage item associations after download. (optional)
    storageConnectionId: str  # UUID of the StorageConnection entity from which to download the media files. Required when downloadStrategy is 'storage_provider'. Used to authenticate and access the source storage provider. (optional)
    credentials: Dict[str, object]  # Decrypted credentials for the storage provider (Fat Payload pattern). Required when downloadStrategy is 'storage_provider'. (optional)
    mediaFiles: List[Dict[str, object]]  # Array of media files to download and process. Must contain at least one file. Each file includes metadata for identification and processing. (optional)
    compressionSettings: Dict[str, object]  # Optional compression settings that override deployment environment defaults. If not provided, uses values from MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, IMAGE_QUALITY, and OUTPUT_FORMAT environment variables. (optional)

class MetamodelMetadataGenerationCompletedMessage(TypedDict, total=False):
    """Handles metamodel metadata generation completion. Contains AI-generated metadata and aggregated technical analysis."""
    metamodelId: str  # The unique identifier for the metamodel
    metadata: Dict[str, object]  # AI-generated metadata for the metamodel
    technicalMetadata: Dict[str, object]  # Aggregated technical analysis from constituent models

class MetamodelMetadataGenerationRequestMessage(TypedDict, total=False):
    """Handles metamodel metadata generation requests via Ollama. Aggregates data from constituent models and generates AI-enhanced metadata."""
    metamodelId: str  # The unique identifier for the metamodel (optional)
    constituentModelIds: List[Dict[str, object]]  # Array of model IDs that compose this metamodel (optional)
    name: str  # The name of the metamodel (optional)
    ownerId: str  # The owner's user ID (optional)
    libraryId: str  # The library containing this metamodel (optional)
    constituentModels: List[Dict[str, object]]  # Enriched metadata for constituent models (includes storage items) (optional)
    webhookUrl: str  # Optional webhook URL for async completion notification (optional)

class ModelAnalyticsCollectionRequestMessage(TypedDict, total=False):
    """Request to collect marketplace analytics for a specific metamodel.
Triggered by backend scheduler every 6 hours for popular/tagged metamodels.

Worker performs targeted market searches based on metamodel metadata
and stores aggregated statistics in Elasticsearch for trend analysis.
"""
    metamodelId: str  # The metamodel ID to collect analytics for
    ownerId: str  # Owner user ID for audit trail
    primaryCategory: str  # Primary classification category (e.g., "miniature", "terrain") (optional)
    subCategory: str  # Sub-category for more specific targeting (optional)
    tags: List[Dict[str, object]]  # Relevant tags from metamodel metadata (max 10) (optional)
    franchise: str  # Franchise name if detected (e.g., "Dungeons & Dragons") (optional)
    confidence: float  # Classification confidence score (optional)
    priority: str  # Collection priority level (optional)
    triggeredBy: str  # Source of trigger (e.g., "backend-scheduler", "manual") (optional)
    triggeredAt: str  # Timestamp when collection was triggered (optional)

class ModelDiscoveryFolderProcessedEventMessage(TypedDict, total=False):
    """Handles model discovery folder processed events."""
    connectionId: str  # The unique identifier for the connection. (optional)
    folderPath: str  # The path to the processed folder. (optional)
    discoveredFiles: List[Dict[str, object]]  # A list of files discovered in the folder. (optional)
    folderSignature: Dict[str, object]  # A signature representing the state of the folder. (optional)
    processedAt: str  # The timestamp when the folder was processed. (optional)
    statistics: Dict[str, object]  # Statistics about the processed folder. (optional)

class ModelDiscoveryScanFoundEventMessage(TypedDict, total=False):
    """Handles model discovery scan found events."""
    modelId: str  # The unique identifier for the model. (optional)
    name: str  # The name of the model. (optional)
    fileName: str  # The name of the model file. (optional)
    description: str  # A description of the model. (optional)
    fileTypes: List[Dict[str, object]]  # An array of file types associated with the model. (optional)
    size: float  # The size of the model file in bytes. (optional)
    storageLocation: Dict[str, object]  # The storage location of the model. (optional)
    providerType: str  # The type of the storage provider. (optional)
    metadata: Dict[str, object]  # A flexible object for additional metadata. (optional)

class ModelDiscoveryScanProgressEventMessage(TypedDict, total=False):
    """Handles model discovery scan progress events."""
    payload: Dict[str, object]  # Contains the discovery scan progress details. (optional)

class ModelDiscoveryScanRequestMessage(TypedDict, total=False):
    """Handles model discovery scan requests events."""
    libraryId: str  # The ID of the library to scan. (optional)
    storageConnectionId: str  # The ID of the storage connection to scan. (optional)
    providerType: str  # The type of the storage provider. (optional)
    path: str  # The specific path within the storage connection to scan for this library. (optional)
    credentials: Dict[str, object]  # Decrypted credentials for the storage provider. (optional)
    configuration: Dict[str, object]  # Configuration for the storage connection (e.g. scanRootPath). (optional)

class ModelFinderIndexRequestMessage(TypedDict, total=False):
    """Request to index a 3D model for similarity search."""
    modelId: str  #  (optional)
    storageItem: object  #  (optional)

class ModelFinderResponseMessage(TypedDict, total=False):
    """Response containing search results from the model finder."""
    requestId: str  #  (optional)
    results: List[Dict[str, object]]  #  (optional)

class ModelFinderSearchRequestMessage(TypedDict, total=False):
    """Request to search for similar 3D models."""
    referenceModelId: str  # Optional: Search using an existing model as reference (optional)
    referenceImageId: str  # Optional: Search using an uploaded image (optional)
    limit: object  #  (optional)

class ModelMetadataGenerationCompletedMessage(TypedDict, total=False):
    """Notifies backend that enriched marketplace metadata generation completed. Backend updates Model entity with generated description, tags, classification, etc."""
    modelId: str  # UUID of the model that was processed.
    metadata: Dict[str, object]  # Enriched marketplace metadata generated by LLM.

class ModelMetadataGenerationRequestMessage(TypedDict, total=False):
    """Generates enriched marketplace metadata (SEO descriptions, tags, categories) for 3D models using LLM vision analysis. Worker receives all necessary data in the payload (Model, TechnicalMetadata, Thumbnails) and does NOT query the database. Prerequisites: file download, technical metadata, and thumbnail generation must be complete before this message is sent."""
    modelId: str  # UUID of the model (reference only) (optional)
    model: Dict[str, object]  # Core model entity data (optional)
    technicalMetadata: Dict[str, object]  # Geometric and technical analysis results (optional)
    thumbnails: List[Dict[str, object]]  # List of 360 degree thumbnail views (URLs or paths) (optional)

class ModelMetamodelDetectionFoundMessage(TypedDict, total=False):
    """Handles model metamodel detection found with hierarchical relationships."""
    metamodels: List[Dict[str, object]]  # List of metamodel nodes in hierarchical structure (roots and children).
    ekgEdges: List[Dict[str, object]]  # EKG edges derived from Louvain clustering (OPTIONAL - new field) (optional)

class ModelMetamodelDetectionRequestMessage(TypedDict, total=False):
    """Handles model metamodel detection requests."""
    connectionId: str  # The unique identifier for the storage connection.
    folderPath: str  # The path to the folder that was processed.
    discoveredFiles: List[Dict[str, object]]  # A list of files discovered in the folder. Worker should check this first, then manifestUrl. (optional)
    manifestUrl: str  # URL to a JSON file containing the list of discovered files (for large folders) (optional)
    folderSignature: Dict[str, object]  # A signature representing the state of the folder.
    processedAt: str  # The timestamp when the folder was processed.
    statistics: Dict[str, object]  # Statistics about the processed folder.

class ModelSellabilityAnalysisCompletedMessage(TypedDict, total=False):
    """Contains sellability analysis results including Etsy-specific recommendations, material pricing, and marketplace compatibility scores"""
    metamodelId: str  # Metamodel UUID (optional)
    ownerId: str  # Owner user ID (optional)
    sellabilityScore: float  # Overall sellability score (0-100) (optional)
    pricingRecommendations: Dict[str, object]  # Pricing analysis and recommendations with material-specific pricing (v2.0.0) (optional)
    marketplaceRecommendations: List[Dict[str, object]]  # Recommended marketplaces with Etsy-specific scoring (v2.0.0) (optional)
    demandAnalysis: Dict[str, object]  # Market demand insights (optional)
    qualityFactors: Dict[str, object]  # Quality-related factors affecting sellability (optional)
    recommendations: List[Dict[str, object]]  # Actionable recommendations to improve sellability (optional)
    analyzedAt: str  # Analysis completion timestamp (ISO 8601) (optional)
    analysisVersion: str  # Analysis algorithm version (optional)
    error: Dict[str, object]  # Error information if analysis failed (optional)

class ModelSellabilityAnalysisRequestMessage(TypedDict, total=False):
    """Analyzes a metamodel to determine sellability score, pricing recommendations, and optimal marketplace selection. Enhanced with Etsy-specific analysis including competitor pricing, category demand trends, and material suitability."""
    metamodelId: str  # UUID of the metamodel to analyze. (optional)
    ownerId: str  # UUID of the user who owns the metamodel (optional)
    metamodelData: Dict[str, object]  # Full metamodel data including technical metadata, enriched metadata, and child models. Injected by backend to avoid DB access. (optional)
    manifestUrl: str  # URL to a JSON manifest containing the metamodel data if it is too large for the message payload. (optional)
    analysisOptions: Dict[str, object]  # Optional analysis configuration (optional)

class ModelSemanticAnalysisCompletedMessage(TypedDict, total=False):
    """Handles completion of 3D model semantic analysis with generated tags and similarity results."""
    modelId: str  # The unique identifier for the model. (optional)
    userId: str  # The user ID who owns the model. (optional)
    processingStatus: str  # Final processing status. (optional)
    semanticMetadata: Dict[str, object]  # Generated semantic metadata and analysis results. (optional)
    processingTime: Dict[str, object]  # Processing performance metrics. (optional)
    qualityMetrics: Dict[str, object]  # Processing quality and confidence metrics. (optional)
    error: Dict[str, object]  # Error information if processing failed. (optional)
    debugInfo: Dict[str, object]  # Additional debug information for troubleshooting. (optional)

class ModelSemanticAnalysisRequestMessage(TypedDict, total=False):
    """Handles 3D model semantic analysis requests using ULIP-2 neural networks and FAISS vector similarity search."""
    modelId: str  # The unique identifier for the model. (optional)
    userId: str  # The user ID who owns the model. (optional)
    storageConnectionId: str  # The ID of the storage connection. (optional)
    filePath: str  # The path to the 3D model file in storage. (optional)
    fileName: str  # The name of the model file. (optional)
    fileSize: float  # The size of the model file in bytes. (optional)
    storageProviderType: str  # The type of the storage provider (S3, GoogleDrive, SFTP, etc). (optional)
    processingOptions: Dict[str, object]  # Configuration options for semantic analysis. (optional)
    priority: float  # Processing priority (1=highest, 10=lowest). (optional)
    webhookUrl: str  # Optional webhook URL for completion notification. (optional)
    retryCount: float  # Current retry attempt number. (optional)

class ModelTechnicalMetadataCompletedMessage(TypedDict, total=False):
    """Reports comprehensive results of technical metadata analysis including geometry, quality metrics, and print-readiness assessment"""
    originalJobId: str  # ID of the original analysis request job (optional)
    modelId: str  # ID of the analyzed model (optional)
    status: str  # Analysis completion status (optional)
    vertices: object  # Number of vertices in the mesh (optional)
    faces: object  # Number of faces/polygons in the mesh (optional)
    edges: object  # Number of edges in the mesh (optional)
    detailLevel: str  # Visual detail level based on polygon density (optional)
    boundingBox: Dict[str, object]  # 3D bounding box dimensions in millimeters (optional)
    volumeCubicMm: float  # Model volume in cubic millimeters (for material calculation) (optional)
    surfaceAreaSqMm: float  # Total surface area in square millimeters (optional)
    minWallThickness: float  # Minimum wall thickness detected in millimeters (critical for printability) (optional)
    maxWallThickness: float  # Maximum wall thickness detected in millimeters (optional)
    manifold: bool  # Is the mesh watertight/manifold? Critical for 3D printing (true = printable) (optional)
    nonManifoldEdges: object  # Number of non-manifold edges (repair needed if > 0) (optional)
    holes: object  # Number of holes/boundary loops in the mesh (0 = closed mesh) (optional)
    flippedNormals: object  # Number of faces with inverted normals (causes rendering/slicing issues) (optional)
    selfIntersections: object  # Number of self-intersecting faces (0 = clean geometry) (optional)
    qualityScore: float  # Overall quality score 0-100 (100 = perfect for printing, <60 needs repair) (optional)
    printabilityScore: float  # Printability score 0-100 (considers supports, orientation, size constraints) (optional)
    requiresSupports: bool  # Does this model require support structures for 3D printing? (optional)
    overhangs: List[Dict[str, object]]  # Detected overhang areas requiring support structures (optional)
    estimatedPrintTimeMinutes: object  # Estimated print time in minutes using normal quality settings (0.2mm layers, 20% infill) (optional)
    printTimeEstimates: Dict[str, object]  # Print time estimates for different quality presets (optional)
    estimatedMaterialGrams: float  # Estimated material usage in grams using 20% infill (assumes PLA density 1.24g/cm³) (optional)
    materialEstimates: Dict[str, object]  # Material usage estimates for different infill percentages (optional)
    recommendedOrientation: Dict[str, object]  # Recommended print orientation for minimal support material and best results (optional)
    originalUnit: str  # Original file format unit detected from metadata or inferred from scale (optional)
    formatVersion: str  # File format version (e.g., 'STL Binary', 'OBJ v4', 'PLY 1.0') (optional)
    hasColorData: bool  # Does the file contain per-vertex color information? (optional)
    hasTextureCoordinates: bool  # Does the file contain UV texture mapping coordinates? (optional)
    hasVertexNormals: bool  # Does the file contain per-vertex normal vectors? (optional)
    analyzedBy: str  # Tool/service that performed the analysis (optional)
    analysisVersion: str  # Version of the analysis algorithm (for tracking improvements) (optional)
    analysisConfidence: float  # Confidence level of analysis results (0.0 = uncertain, 1.0 = highly confident) (optional)
    analysisWarnings: List[Dict[str, object]]  # Warnings or issues detected during analysis (structured for programmatic handling) (optional)
    analyzedAt: str  # ISO 8601 timestamp when analysis was performed (e.g., '2025-11-19T14:35:22Z') (optional)
    errorMessage: str  # Detailed error message if status is FAILED (optional)
    errorCode: str  # Machine-readable error code for programmatic error handling (optional)

class ModelTechnicalMetadataRequestMessage(TypedDict, total=False):
    """Triggers comprehensive technical analysis of a 3D model file to extract geometry, quality metrics, and print-readiness information"""
    modelId: str  # Unique identifier for the model to analyze (optional)
    ownerId: str  # User ID who owns the model (optional)
    storageLocation: Dict[str, object]  # Location of the 3D model file (legacy - used for direct download if minioPath not provided) (optional)
    minioPath: str  # Path to model in MinIO (e.g., 'raw_models/{modelId}/original.glb'). If provided, file will be read from MinIO instead of downloading from storage provider. (optional)
    parentJobId: str  # ID of parent file-download job (for BullMQ dependency tracking). (optional)
    analysisOptions: Dict[str, object]  # Optional analysis configuration parameters (optional)

class ThumbnailGenerationCompletedMessage(TypedDict, total=False):
    """Handles thumbnail generation completed."""
    originalJobId: str  # The ID of the original job that requested the thumbnail generation. (optional)
    modelId: str  # The ID of the model that the thumbnail was generated for. (optional)
    status: str  # The status of the thumbnail generation. (optional)
    thumbnailPath: str  # The path to the generated thumbnail. (optional)
    thumbnail360Views: List[Dict[str, object]]  # Array of 360° thumbnail view paths (16 angles) for vision-based analysis. (optional)
    gltfPreviewPath: str  # The path to the generated GLTF/GLB 3D preview file. (optional)
    errorMessage: str  # An error message if the thumbnail generation failed. (optional)
    storageLocation: Dict[str, object]  # The storage location of the model. (optional)

class ThumbnailGenerationRequestMessage(TypedDict, total=False):
    """Handles thumbnail generation requests with customization options. Supports both storage provider downloads and MinIO-cached files."""
    modelId: str  # The unique identifier for the model requiring a thumbnail. (optional)
    ownerId: str  # The identifier of the user who owns the entity. (optional)
    storageLocation: Dict[str, object]  # The storage location of the model (legacy - used for direct download if minioPath not provided). (optional)
    minioPath: str  # Path to model in MinIO (e.g., 'raw_models/{modelId}/original.glb'). If provided, file will be read from MinIO instead of downloading from storage provider. (optional)
    previewType: str  # The type of preview to generate, e.g., 'default', 'static', 'glb'. (optional)
    generate360Views: bool  # Generate 16 angle views for 360° preview (4 horizontal x 4 vertical angles) for enhanced vision-based metadata analysis. (optional)
    parentJobId: str  # ID of parent file-download job (for BullMQ dependency tracking). (optional)
    customization: Dict[str, object]  # User-defined customizations for the thumbnail. (optional)

class UserEngagementEventMessage(TypedDict, total=False):
    """User engagement and onboarding tracking events for analytics and behavioral insights.

Captures key user actions throughout their journey:
- Account creation and onboarding steps
- Feature usage and adoption
- Model management activities
- Marketplace interactions
- Subscription changes

Used for:
- User onboarding funnel analysis
- Feature adoption tracking
- User retention metrics
- A/B testing and experimentation
- Personalization and recommendations
- Product analytics dashboards
"""
    eventType: str  # Category of user engagement event
    action: str  # Specific user action performed
    timestamp: str  # ISO 8601 timestamp when the action occurred
    userId: str  # Unique identifier of the user
    userEmail: str  # User's email (hashed for privacy in analytics) (optional)
    userCreatedAt: str  # When the user account was created (for cohort analysis) (optional)
    userPlanTier: str  # Current subscription plan tier (optional)
    sessionId: str  # User session identifier for grouping actions (optional)
    requestId: str  # Request ID for correlation with logs (optional)
    actionDetails: Dict[str, object]  # Additional context about the action (optional)
    source: str  # Where the action originated (optional)
    httpMethod: str  # HTTP method used (optional)
    httpUrl: str  # API endpoint path (optional)
    httpStatusCode: object  # HTTP response status code (optional)
    durationMs: float  # Action duration in milliseconds (optional)
    experimentId: str  # A/B test or experiment ID (optional)
    experimentVariant: str  # Experiment variant/group (optional)
    environment: str  # Deployment environment (optional)
    clientInfo: Dict[str, object]  # Client/browser information (anonymized) (optional)

class WorkerAnalyticsEventMessage(TypedDict, total=False):
    """Analytics event emitted by workers for tracking processing metrics, user behavior,
and model statistics. Consumed by worker-analytic-collector and forwarded to ELK.

All workers MUST emit this event upon job completion (success or failure).
Each worker includes its specific metrics in the `metrics` object.
"""
    eventType: str  # Type of analytics event
    workerId: str  # Identifier of the worker that processed the job
    jobId: str  # Unique job identifier from BullMQ
    timestamp: str  # ISO 8601 timestamp of event emission
    userId: str  # User who owns the model/triggered the job (optional)
    modelId: str  # Model identifier (if applicable) (optional)
    metamodelId: str  # Metamodel identifier (if applicable) (optional)
    storageItemId: str  # Storage item identifier (for download events) (optional)
    status: str  # Job completion status (optional)
    errorCode: str  # Error code if status is failure (optional)
    errorMessage: str  # Error message if status is failure (optional)
    timing: Dict[str, object]  # Processing time metrics in milliseconds (optional)
    metrics: Dict[str, object]  # Worker-specific metrics. Structure varies by eventType. (optional)

class WorkerMetricsEnrichedEventMessage(TypedDict, total=False):
    """Enriched metrics event for detailed worker monitoring, cost tracking,
and performance analysis. Published to backend.logging.events for
centralized monitoring and cost attribution.

This event is emitted by all workers on job completion and includes:
- LLM token usage and cost breakdown
- System resource consumption (CPU, RAM, disk I/O)
- Detailed timing breakdown by stage
- User and context attribution
- Model-specific metadata
"""
    eventType: str  # Fixed type for enriched worker metrics
    workerId: str  # Identifier of the worker
    jobId: str  # Unique BullMQ job identifier
    timestamp: str  # ISO 8601 timestamp when job completed
    status: str  # Job completion status
    userId: str  # User who owns the resource/triggered the job (optional)
    tenantId: str  # Organization/tenant ID (for multi-tenant deployments) (optional)
    sessionId: str  # Session ID for correlating user actions (optional)
    requestId: str  # Request ID from originating API call (X-Request-Id) (optional)
    modelId: str  # Model ID being processed (optional)
    metamodelId: str  # Metamodel ID being processed (optional)
    storageItemId: str  # Storage item ID (for file operations) (optional)
    timing: Dict[str, object]  # Comprehensive timing breakdown (optional)
    llmUsage: Dict[str, object]  # LLM token usage and cost breakdown (optional)
    resources: Dict[str, object]  # System resource consumption during job (optional)
    workerMetrics: Dict[str, object]  # Worker-specific metrics (varies by worker type) (optional)
    error: Dict[str, object]  # Error details if status is failure (optional)
    environment: str  # Deployment environment (optional)
    region: str  # Cloud region/datacenter (optional)
    workerVersion: str  # Worker service version (optional)
    hostname: str  # Pod/container hostname (optional)

