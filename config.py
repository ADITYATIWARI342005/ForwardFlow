# CNCF Issue Tracker Configuration
# Edit this file to customize your bot settings

# Your 10 repositories to monitor (format: "owner/repo")
REPOSITORIES = [
    "kubernetes/kubernetes",
    "prometheus/prometheus",
    "prometheus/alertmanager",
    "prometheus/client_golang",
    "prometheus-community/helm-charts",
    "istio/istio",
    "istio/community",
    "istio/istio.io",
    "jaegertracing/helm-charts",
    "jaegertracing/jaeger",
    "jaegertracing/jaeger-ui",
    "jaegertracing/jaeger-operator",
    "cilium/cilium",
    "cilium/ebpf",
    "cilium/tetragon",
    "cilium/cilium-cli",
]

# Check interval in seconds (60-240 seconds = 1-4 minutes)
DEFAULT_CHECK_INTERVAL = 180  # 3 minutes

# Database file path
DATABASE_PATH = "cncf_issues.db"

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Batch size for processing repositories (to avoid overwhelming APIs)
BATCH_SIZE = 3

# Delay between batches in seconds
BATCH_DELAY = 2

# Rate limiting delay between issue notifications in seconds
NOTIFICATION_DELAY = 1

# Timeout for API requests in seconds
API_TIMEOUT = 10

# Buffer time for issue checking (minutes added to check interval)
CHECK_BUFFER_MINUTES = 2
