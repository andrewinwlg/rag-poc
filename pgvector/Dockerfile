FROM postgres:15

# Install dependencies for building pgvector
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-15 \
    make \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone and build pgvector extension
RUN git clone https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/ 