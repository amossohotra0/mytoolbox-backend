# MyToolbox

MyToolbox is a Django-based web application providing a suite of document processing APIs, with a focus on PDF manipulation. The project includes endpoints for merging, splitting, encrypting, and performing OCR on PDF files, built with a modular architecture and documented using `drf-spectacular` for Swagger UI and ReDoc.

This README guides developers on setting up the project locally for development and testing.

## Features

- **Merge PDF**: Combine multiple PDF files into a single PDF (`/api/merge-pdf/`).
- **Split PDF**: Extract specified page ranges from a PDF (`/api/split-pdf/`).
- **Split PDF by Page**: Split a PDF into individual PDFs, one per page, returned as a ZIP file (`/api/split-pdf-by-page/`).
- **Encrypt PDF**: Add password protection to a PDF (`/api/encrypt-pdf/`).
- **OCR PDF**: Extract text from PDFs using OCR, with output as JSON or a `.txt` file (`/api/ocr-pdf/`).

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8+**: Check with `python3 --version` or `python --version`.
- **pip**: Python package manager, included with Python.
- **Virtualenv** (recommended): For isolating dependencies (`pip install virtualenv`).
- **Tesseract-OCR**: Required for the OCR PDF API.
  - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
  - **CentOS/RHEL**: `sudo yum install tesseract`
  - **macOS**: `brew install tesseract`
  - **Windows**: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.
  - Verify: `tesseract --version`
- **Git**: For cloning the repository (`git --version`).
- A code editor (e.g., VS Code, PyCharm).

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
└── README.md             # This file
```

## Setup Instructions

Follow these steps to set up the project locally on Linux, macOS, or Windows.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mytoolbox
```

Replace `<repository-url>` with the URL of your Git repository.

### 2. Create and Activate a Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs Django, DRF, `pdfplumber`, `pytesseract`, `PyPDF2`, and other dependencies.

### 4. Configure the Project

No database migrations are required, as the project uses no models. However, collect static files for Swagger UI and ReDoc:

```bash
python manage.py collectstatic
```

This creates a `static/` directory (default: `E:/mytoolbox/static/` on Windows; adjust `STATIC_ROOT` in `project/settings.py` if needed).

### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will run at `http://localhost:8000`. Access the API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

### 6. Test the APIs

Use curl, Postman, or Swagger UI to test the APIs. Example commands:

- **Merge PDF**:
  ```bash
  curl -X POST -F "pdf_files=@file1.pdf" -F "pdf_files=@file2.pdf" http://localhost:8000/api/merge-pdf/ --output merged.pdf
  ```

- **Split PDF** (e.g., pages 1-2, 4):
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

Test with valid, non-encrypted PDFs. For OCR, use PDFs with clear text or scannable images.

## Troubleshooting

- **Tesseract not found**:
  - Ensure `tesseract-ocr` is installed and in your PATH.
  - Verify: `tesseract --version`.
  - Install language packs if needed: `sudo apt-get install tesseract-ocr-eng`.

- **Static files not loading in Swagger UI/ReDoc**:
  - Re-run `python manage.py collectstatic`.
  - Check `STATIC_ROOT` in `project/settings.py` and ensure write permissions.

- **OCR returns no text**:
  - Test with a text-based or high-quality scanned PDF.
  - Increase `resolution` in `pdf_tools/processors.py` (e.g., from 300 to 600).

- **Server errors**:
  - Check the terminal output for detailed error messages.
  - Ensure all dependencies are installed (`pip install -r requirements.txt`).

- **Windows PATH issues**:
  - Add Tesseract to PATH manually (e.g., `C:\Program Files\Tesseract-OCR\`).
  - Restart your terminal after updating PATH.

## Deployment Notes (Linux Server)

For production deployment on a Linux server (e.g., Ubuntu):

1. **Set up the server**:
   - Install Python, `tesseract-ocr`, and a web server (e.g., Nginx).
   - Clone the repository and install dependencies as above.

2. **Configure Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn --workers 3 --bind 0.0.0.0:8000 project.wsgi
   ```

3. **Set up Nginx**:
   - Configure Nginx to proxy requests to Gunicorn.
   - Example `/etc/nginx/sites-available/mytoolbox`:
     ```
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

4. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

5. **Secure with SSL**:
   - Use Certbot for Let’s Encrypt: `sudo apt-get install certbot python3-certbot-nginx`.

6. **Consider Celery**:
   - For large PDFs, use Celery for async processing (see `CELERY_BROKER_URL` in `project/settings.py`).

For detailed deployment, refer to Django’s deployment checklist.

## Contributing

- Fork the repository and create a branch for your feature or bugfix.
- Write tests in `api/tests.py` or relevant app’s `tests.py`.
- Submit a pull request with a clear description of changes.

## License

[Specify your license, e.g., MIT License]

---

For issues or questions, contact [your contact info or repository issues page].