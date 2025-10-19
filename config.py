#!/usr/bin/env python3
"""
Configuration file for CNCF Issue Tracker Bot
Contains repository list and default settings.
"""

# Repository list to monitor
REPOSITORIES = [
    "prometheus/prometheus",
    "prometheus/client_golang", 
    "open-telemetry/opentelemetry-collector-contrib",
    "prometheus/docs",
    "envoyproxy/gateway",
    "envoyproxy/envoy",
    "jaegertracing/jaeger",
    "jaegertracing/jaeger-operator",
    "jaegertracing/helm-charts",
    "jaegertracing/documentation",
    "jaegertracing/jaeger-ui",
    "cilium/cilium.io",
    "cilium/cilium",
    "cilium/hubble-ui"
]

# Default configuration values
DEFAULT_CHECK_INTERVAL = 60  # 1 minute for more real-time feel
DATABASE_PATH = "cncf_issues.db"
LOG_LEVEL = "INFO"
BATCH_SIZE = 3
BATCH_DELAY = 2
NOTIFICATION_DELAY = 1
API_TIMEOUT = 10
CHECK_BUFFER_MINUTES = 2