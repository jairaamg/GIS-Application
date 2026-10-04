FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.2

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages || \
    pip3 install --no-cache-dir -r requirements.txt

COPY . /app/workers/gdal_worker
WORKDIR /app
CMD ["python3", "-m", "workers.gdal_worker"]
