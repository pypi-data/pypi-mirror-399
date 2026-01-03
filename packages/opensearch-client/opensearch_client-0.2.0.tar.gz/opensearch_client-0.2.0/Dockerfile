FROM opensearchproject/opensearch:3.0.0

LABEL org.opencontainers.image.source="https://github.com/namyoungkim/opensearch-client"
LABEL org.opencontainers.image.description="OpenSearch with Korean (Nori) analyzer plugin"
LABEL org.opencontainers.image.licenses="MIT"

# Install Nori Korean analyzer plugin
RUN /usr/share/opensearch/bin/opensearch-plugin install --batch analysis-nori
