# Deployment Guide

## Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd document-analysis
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following contents:
```
FLASK_APP=document_analysis
FLASK_ENV=development
GEMINI_API_KEY=your_api_key_here
```

5. Initialize database:
```bash
flask init-db
```

6. Run development server:
```bash
flask run
```

## Production Deployment

### Using Gunicorn and Nginx

1. Install production dependencies:
```bash
pip install gunicorn
```

2. Create systemd service file `/etc/systemd/system/document-analysis.service`:
```ini
[Unit]
Description=Document Analysis Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/document-analysis
Environment="PATH=/path/to/document-analysis/venv/bin"
Environment="FLASK_APP=document_analysis"
Environment="FLASK_ENV=production"
Environment="GEMINI_API_KEY=your_api_key_here"
ExecStart=/path/to/document-analysis/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 'document_analysis:create_app()'

[Install]
WantedBy=multi-user.target
```

3. Configure Nginx `/etc/nginx/sites-available/document-analysis`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/document-analysis/document_analysis/static;
    }
}
```

4. Enable and start services:
  
```bash
sudo systemctl enable document-analysis
sudo systemctl start document-analysis
sudo ln -s /etc/nginx/sites-available/document-analysis /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

ENV FLASK_APP=document_analysis
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "document_analysis:create_app()"]
```

Create `docker-compose.yml`:
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - GEMINI_API_KEY=your_api_key_here
```

Deploy with Docker:
```bash
docker-compose up -d
```