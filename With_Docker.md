# MyToolbox

**MyToolbox** is a Django-based web application providing a suite of document processing APIs, focused on PDF manipulation. Built with a modular architecture, it includes endpoints for merging, splitting, encrypting, and performing OCR on PDF files, with API documentation via `drf-spectacular` (Swagger UI and ReDoc).

This README guides developers on setting up the project using Docker for consistent development and deployment across environments.

## Features

- **Merge PDF**: Combines multiple PDFs into one (`/api/merge-pdf/`).
- **Split PDF**: Extracts specified page ranges from a PDF (`/api/split-pdf/`).
- **Split PDF by Page**: Splits a PDF into individual PDFs, one per page, as a ZIP file (`/api/split-pdf-by-page/`).
- **Encrypt PDF**: Adds password protection to a PDF (`/api/encrypt-pdf/`).
- **OCR PDF**: Extracts text using OCR, returning JSON or a `.txt` file (`/api/ocr-pdf/`).

## Prerequisites

Ensure the following are installed before setup:

- **Docker**: For containerization.
  - *Linux*: `sudo apt-get install docker.io`
  - *Windows/macOS*: Install Docker Desktop.
  - Verify: `docker --version`.
- **Docker Compose**: For managing multi-container setups.
  - *Linux*: `sudo apt-get install docker-compose`
  - *Windows/macOS*: Included with Docker Desktop.
  - Verify: `docker-compose --version`.
- **Git**: For cloning the repository.
  - Install: `sudo apt-get install git` (Linux) or equivalent.
  - Verify: `git --version`.
- A code editor *(e.g., VS Code, PyCharm)*.

## Project Structure

```
mytoolbox/
├── manage.py
├── project/              # Django project settings
├── api/                  # API endpoints and serializers
├── pdf_tools/            # PDF processing logic
├── security_tools/       # Security-related processing (e.g., encryption)
├── word_tools/           # Placeholder for Word-related tools
├── ppt_tools/            # Placeholder for PowerPoint tools
├── excel_tools/          # Placeholder for Excel tools
├── image_tools/          # Placeholder for image tools
├── organize_tools/       # Placeholder for organization tools
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration for the Django app
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

## Setup Instructions

The project is set up using Docker to ensure consistency across development and production environments.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mytoolbox
```

> Replace `<repository-url>` with your Git repository URL.

### 2. Build and Run with Docker Compose

Build the Docker image and start the Django server:

```bash
docker-compose up --build
```

This:

- Builds the Django app image using `Dockerfile`.
- Installs `tesseract-ocr` and project dependencies.
- Runs the Django development server on port 8000.
- Collects static files for Swagger UI/ReDoc.

Access the server at `http://localhost:8000`. API documentation:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

To run in detached mode:

```bash
docker-compose up --build -d
```

Stop the containers:

```bash
docker-compose down
```

### 3. Collect Static Files (Optional)

Static files are collected during the Docker build. If you modify static assets:

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

> **Note**: The Docker setup mounts the project directory, so code changes are reflected without rebuilding. Restart the container (`docker-compose restart`) if needed.

## Testing the APIs

Use curl, Postman, or Swagger UI to test the APIs. Example commands:

- **Merge PDF**:

  ```bash
  curl -X POST -F "pdf_files=@file1.pdf" -F "pdf_files=@file2.pdf" http://localhost:8000/api/merge-pdf/ --output merged.pdf
  ```

- **Split PDF** (pages 1-2, 4):

  ```bash
  curl -X POST -F "pdf_file=@input.pdf" -F "page_ranges=1-2,4" http://localhost:8000/api/split-pdf/ --output split.pdf
  ```

- **Split PDF by Page**:

  ```bash
  curl -X POST -F "pdf_file=@input.pdf" http://localhost:8000/api/split-pdf-by-page/ --output split_pages.zip
  ```

- **Encrypt PDF**:

  ```bash
  curl -X POST -F "pdf_file=@input.pdf" -F "password=mypassword" http://localhost:8000/api/encrypt-pdf/ --output encrypted.pdf
  ```

- **OCR PDF** (JSON output):

  ```bash
  curl -X POST -F "pdf_file=@document.pdf" http://localhost:8000/api/ocr-pdf/
  ```

- **OCR PDF** (text file output):

  ```bash
  curl -X POST -F "pdf_file=@document.pdf" -F "format=txt" http://localhost:8000/api/ocr-pdf/ --output extracted_text.txt
  ```

> **Note**: Use valid, non-encrypted PDFs. For OCR, test with text-based or high-quality scanned PDFs.

## Troubleshooting

- **Docker build fails**:

  - Check `Dockerfile` and `requirements.txt` for errors.
  - Ensure Docker has enough memory (adjust in Docker Desktop settings).
  - Clear cached images: `docker-compose build --no-cache`.

- **Tesseract errors**:

  - Verify `tesseract-ocr` is installed in the Docker image: `docker-compose exec web tesseract --version`.
  - Check for language packs in the `Dockerfile` (`tesseract-ocr-eng`).

- **Static files not loading**:

  - Run `docker-compose exec web python manage.py collectstatic --noinput`.
  - Verify `STATIC_ROOT` in `project/settings.py` and volume mapping in `docker-compose.yml`.

- **OCR returns no text**:

  - Test with a text-based or high-quality scanned PDF.
  - Increase `resolution` in `pdf_tools/processors.py` (e.g., from 300 to 600).

- **Server errors**:

  - Check logs: `docker-compose logs web`.
  - Rebuild the image: `docker-compose up --build`.

## Deployment Notes (Linux Server)

For production deployment on a Linux server (e.g., Ubuntu) using Docker:

1. **Set up the server**:

   - Install Docker and Docker Compose:

     ```bash
     sudo apt-get update
     sudo apt-get install docker.io docker-compose
     ```

   - Clone the repository:

     ```bash
     git clone <repository-url>
     cd mytoolbox
     ```

2. **Configure Environment**:

   - Create a `.env` file for production settings:

     ```bash
     echo "DEBUG=False" > .env
     ```

3. **Run with Docker Compose**:

   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

4. **Set up Nginx**:

   - Install Nginx: `sudo apt-get install nginx`.

   - Create `/etc/nginx/sites-available/mytoolbox`:

     ```nginx
     server {
         listen 80;
         server_name your-domain.com;
         location / {
             proxy_pass http://127.0.0.1:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
         location /static/ {
             alias /path/to/mytoolbox/static/;
         }
     }
     ```

   - Enable: `sudo ln -s /etc/nginx/sites-available/mytoolbox /etc/nginx/sites-enabled/`

   - Restart Nginx: `sudo systemctl restart nginx`

5. **Secure with SSL**:

   - Install Certbot: `sudo apt-get install certbot python3-certbot-nginx`.
   - Run: `sudo certbot --nginx`.

6. **Optional: Use Celery**:

   - Add a Redis service to `docker-compose.yml`:

     ```yaml
     redis:
       image: redis:7
       networks:
         - mytoolbox
     ```

   - Configure `CELERY_BROKER_URL` in `project/settings.py` (e.g., `redis://redis:6379/0`).

   - Add a Celery worker service:

     ```yaml
     celery:
       build: .
       command: celery -A project worker --loglevel=info
       volumes:
         - .:/app
       depends_on:
         - redis
       networks:
         - mytoolbox
     ```

Refer to Django’s deployment checklist for additional production considerations.

## Contributing

- Fork the repository and create a feature/bugfix branch.
- Add tests in `api/tests.py` or relevant app’s `tests.py`.
- Submit a pull request with a clear description.

## License

\[MIT License\] *(Update with your preferred license)*

---

For issues or questions, open an issue on the repository or contact \[your contact info\].