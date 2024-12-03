from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import *
from pdf_tools.processors import *
from django.http import FileResponse

class MergePDFView(APIView):
    @extend_schema(
        request=MergePDFSerializer,
        responses={
            200: OpenApiResponse(description="Merged PDF file"),
            400: OpenApiResponse(description="Invalid input or invalid PDF files"),
            500: OpenApiResponse(description="Server error during PDF processing")
        },
        summary="Merge multiple PDF files",
        description="Combines multiple PDF files into a single PDF document. All files must be valid, non-encrypted PDFs."
    )
    def post(self, request):
        serializer = MergePDFSerializer(data=request.data)
        if serializer.is_valid():
            pdf_files = serializer.validated_data['pdf_files']
            try:
                merged_pdf = merge_pdfs(pdf_files)
                return FileResponse(
                    merged_pdf,
                    as_attachment=True,
                    filename='merged.pdf',
                    content_type='application/pdf'
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Server error during PDF processing: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SplitPDFView(APIView):
    @extend_schema(
        request=SplitPDFSerializer,
        responses={
            200: OpenApiResponse(description="Split PDF file"),
            400: OpenApiResponse(description="Invalid input, invalid PDF file, or invalid page ranges"),
            500: OpenApiResponse(description="Server error during PDF processing")
        },
        summary="Split a PDF into specified pages",
        description="Extracts specified page ranges from a PDF into a new PDF. Page ranges should be in the format '1-3,5'. The input PDF must be valid and non-encrypted."
    )
    def post(self, request):
        serializer = SplitPDFSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf_file']
            page_ranges = serializer.validated_data['page_ranges']
            try:
                split_pdf_file = split_pdf(pdf_file, page_ranges)
                return FileResponse(
                    split_pdf_file,
                    as_attachment=True,
                    filename='split.pdf',
                    content_type='application/pdf'
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Server error during PDF processing: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SplitPDFByPageView(APIView):
    @extend_schema(
        request=SplitPDFByPageSerializer,
        responses={
            200: OpenApiResponse(description="ZIP file containing one PDF per page"),
            400: OpenApiResponse(description="Invalid input or invalid PDF file"),
            500: OpenApiResponse(description="Server error during PDF processing")
        },
        summary="Split a PDF into one PDF per page",
        description="Splits a PDF into individual PDFs, one for each page, and returns them as a ZIP file. The input PDF must be valid and non-encrypted."
    )
    def post(self, request):
        serializer = SplitPDFByPageSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf_file']
            try:
                zip_file = split_pdf_by_page(pdf_file)
                return FileResponse(
                    zip_file,
                    as_attachment=True,
                    filename='split_pages.zip',
                    content_type='application/zip'
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Server error during PDF processing: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EncryptPDFView(APIView):
    @extend_schema(
        request=EncryptPDFSerializer,
        responses={
            200: OpenApiResponse(description="Encrypted PDF file"),
            400: OpenApiResponse(description="Invalid input or invalid PDF file"),
            500: OpenApiResponse(description="Server error during PDF encryption")
        },
        summary="Encrypt a PDF file with a password",
        description="Encrypts a PDF file with a user-provided password and returns the encrypted PDF. The input PDF must be valid."
    )
    def post(self, request):
        serializer = EncryptPDFSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf_file']
            password = serializer.validated_data['password']
            try:
                encrypted_pdf = encrypt_pdf(pdf_file, password)
                return FileResponse(
                    encrypted_pdf,
                    as_attachment=True,
                    filename='encrypted.pdf',
                    content_type='application/pdf'
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Server error during PDF encryption: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OCRPDFView(APIView):
    @extend_schema(
        request=OCRPDFSerializer,
        responses={
            200: OpenApiResponse(description="Extracted text as JSON or text file"),
            400: OpenApiResponse(description="Invalid input or invalid PDF file"),
            500: OpenApiResponse(description="Server error during OCR processing")
        },
        summary="Perform OCR on a PDF file",
        description="Extracts text from a PDF file using OCR. Use 'format=json' for JSON response (default) or 'format=txt' for a downloadable text file. The input PDF must be valid and non-encrypted."
    )
    def post(self, request):
        serializer = OCRPDFSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf_file']
            response_format = serializer.validated_data['format']
            try:
                text_content = ocr_pdf(pdf_file)
                if response_format == 'txt':
                    # Create a text file in memory
                    txt_buffer = BytesIO()
                    txt_buffer.write(text_content.encode('utf-8'))
                    txt_buffer.seek(0)
                    return FileResponse(
                        txt_buffer,
                        as_attachment=True,
                        filename='extracted_text.txt',
                        content_type='text/plain'
                    )
                return Response(
                    {'text': text_content},
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Server error during OCR processing: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)