"""PDF generation service.

Provides invoice PDF generation using Jinja2 templates and WeasyPrint.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from pydantic_invoices.schemas import Invoice  # type: ignore[import-untyped]


class PDFService:
    """Service for generating PDF invoices from templates.

    This service uses Jinja2 for templating and WeasyPrint for PDF generation.
    """

    def __init__(
        self,
        template_dir: str = "templates",
        output_dir: str = "output",
        default_template: str = "invoice.html.j2",
    ):
        """Initialize PDF service.

        Args:
            template_dir: Directory containing Jinja2 templates
            output_dir: Directory for generated PDF files
            default_template: Default template filename

        Raises:
            ImportError: If jinja2 is not installed
        """
        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            raise ImportError(
                "Jinja2 is required for PDF generation. "
                "Install it with: pip install py-invoices[pdf]"
            )

        self.template_dir = template_dir
        self.output_dir = output_dir
        self.default_template = default_template

        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        self.env: Environment = Environment(loader=FileSystemLoader(template_dir))

    def generate_html(
        self,
        invoice: Invoice,
        company: dict[str, Any],
        template_name: str | None = None,
        logo_path: str | None = None,
        **context: Any,
    ) -> str:
        """Generate HTML from invoice data.

        Args:
            invoice: Invoice schema instance
            company: Company information dictionary
            template_name: Template to use (defaults to default_template)
            logo_path: Optional path to company logo
            **context: Additional template context variables

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template(template_name or self.default_template)

        return template.render(
            invoice=invoice,
            company=company,
            logo_path=logo_path,
            **context,
        )

    def generate_pdf(
        self,
        invoice: Invoice,
        company: dict[str, Any],
        output_filename: str | None = None,
        template_name: str | None = None,
        logo_path: str | None = None,
        **context: Any,
    ) -> str:
        """Generate PDF for an invoice and save to file.

        Args:
            invoice: Invoice schema instance
            company: Company information dictionary
            output_filename: Custom output filename (defaults to invoice number)
            template_name: Template to use (defaults to default_template)
            logo_path: Optional path to company logo
            **context: Additional template context variables

        Returns:
            Path to generated PDF file

        Raises:
            ImportError: If WeasyPrint is not installed or system dependencies missing
        """
        # Generate PDF bytes
        pdf_bytes = self.generate_pdf_bytes(
            invoice=invoice,
            company=company,
            template_name=template_name,
            logo_path=logo_path,
            **context,
        )

        # Determine output path
        if not output_filename:
            output_filename = f"{invoice.number}.pdf"

        output_path = os.path.join(self.output_dir, output_filename)

        # Save PDF
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        return output_path

    def generate_pdf_bytes(
        self,
        invoice: Invoice,
        company: dict[str, Any],
        template_name: str | None = None,
        logo_path: str | None = None,
        **context: Any,
    ) -> bytes:
        """Generate PDF for an invoice and return as bytes.

        Args:
            invoice: Invoice schema instance
            company: Company information dictionary
            template_name: Template to use (defaults to default_template)
            logo_path: Optional path to company logo
            **context: Additional template context variables

        Returns:
            Raw PDF bytes

        Raises:
            ImportError: If WeasyPrint is not installed or system dependencies missing
        """
        try:
            from weasyprint import HTML  # type: ignore[import-untyped]
        except (ImportError, OSError):
            raise ImportError(
                "WeasyPrint is required for PDF generation but was not found or "
                "is missing system dependencies (like pango). "
                "Install it with: pip install py-invoices[pdf] "
                "On macOS, you may also need: brew install pango libffi"
            )

        # Generate HTML
        html_content = self.generate_html(
            invoice=invoice,
            company=company,
            template_name=template_name,
            logo_path=logo_path,
            **context,
        )

        # Generate PDF
        pdf_bytes = HTML(
            string=html_content, base_url=os.path.abspath(self.template_dir)
        ).write_pdf()

        if pdf_bytes is None:
            raise RuntimeError("Failed to generate PDF bytes")

        from typing import cast

        return cast(bytes, pdf_bytes)

    def save_html(
        self,
        invoice: Invoice,
        company: dict[str, Any],
        output_filename: str | None = None,
        template_name: str | None = None,
        logo_path: str | None = None,
        **context: Any,
    ) -> str:
        """Save invoice as HTML file (fallback when PDF generation fails).

        Args:
            invoice: Invoice schema instance
            company: Company information dictionary
            output_filename: Custom output filename (defaults to invoice number)
            template_name: Template to use (defaults to default_template)
            logo_path: Optional path to company logo
            **context: Additional template context variables

        Returns:
            Path to generated HTML file
        """
        # Generate HTML
        html_content = self.generate_html(
            invoice=invoice,
            company=company,
            template_name=template_name,
            logo_path=logo_path,
            **context,
        )

        # Determine output path
        if not output_filename:
            output_filename = f"{invoice.number}.html"

        output_path = os.path.join(self.output_dir, output_filename)

        # Save HTML
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path
