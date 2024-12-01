from rest_framework import serializers

class MergePDFSerializer(serializers.Serializer):
    pdf_files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True,
        help_text="List of PDF files to merge"
    )

class SplitPDFSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        write_only=True,
        help_text="PDF file to split"
    )
    page_ranges = serializers.CharField(
        write_only=True,
        help_text="Page ranges to extract (e.g., '1-3,5')"
    )

    def validate_page_ranges(self, value):
        """Validate page range format and values."""
        try:
            ranges = value.split(',')
            for range_str in ranges:
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    if start < 1 or end < start:
                        raise ValueError
                else:
                    page = int(range_str)
                    if page < 1:
                        raise ValueError
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                "Invalid page ranges. Use format '1-3,5' with positive integers."
            )
        return value

class SplitPDFByPageSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        write_only=True,
        help_text="PDF file to split into one PDF per page"
    )

class EncryptPDFSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        write_only=True,
        help_text="PDF file to encrypt"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Password to lock the PDF"
    )

    def validate_password(self, value):
        """Ensure password is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Password cannot be empty.")
        return value

class OCRPDFSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        write_only=True,
        help_text="PDF file to perform OCR on"
    )
    format = serializers.ChoiceField(
        choices=['json', 'txt'],
        default='json',
        required=False,
        help_text="Response format: 'json' for text in JSON, 'txt' for text file"
    )
