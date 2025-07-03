"""Kolosal Server PDF Parsing Test"""
import io
import base64
import time
import asyncio
from typing import Optional, List
import requests
import aiohttp
import PyPDF2
from tests.kolosal_tests import KolosalTestBase


class ParsePDFTest(KolosalTestBase):
    """Test class for PDF parsing functionality in Kolosal Server."""

    def test_parse_pdf(self,
                       path: Optional[str] = "test_files/test_pdf.pdf",
                       method: Optional[str] = "fast") -> None:
        """Test parsing a PDF file."""
        # Status Report
        print(f"🚀 Testing PDF parsing: {path}")
        print("⏳ Sending request...")

        initial_time = time.time()

        # Open the PDF file and send it to the Kolosal Server for parsing
        with open(path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(pdf_reader.pages)
            b64_pdf = base64.b64encode(pdf_bytes).decode()

        # Send the PDF to the Kolosal Server for parsing
        api_url = f"{self.client.base_url}/parse_pdf"

        payload = {
            "data": b64_pdf,
            "method": method
        }

        response = requests.post(api_url, json=payload, timeout=30)
        elapsed_time = time.time() - initial_time

        assert response.status_code == 200, "Failed to parse PDF file."

        # Extract page count from response
        _result = response.json()

        pages_per_second = total_pages / elapsed_time if elapsed_time > 0 else 0

        # Status Report
        print("✅ PDF parsing completed!")
        print(f"📄 Total pages: {total_pages}")
        print(f"⏱️ Time per PDF: {elapsed_time:.2f} seconds")
        print(f"🔥 Pages per second: {pages_per_second:.2f}")
        print("")

    def concurrent_parse_pdf(self,
                             pdf_paths: Optional[List[str]] = None,
                             method: Optional[str] = "fast") -> None:
        """Test concurrent PDF parsing requests using asyncio."""

        if pdf_paths is None:
            pdf_paths = [
                "test_files/test_pdf.pdf",
                "test_files/test_pdf2.pdf",
                "test_files/test_pdf3.pdf",
                "test_files/test_pdf4.pdf",
                "test_files/test_pdf5.pdf"
            ]

        print(
            f"🚀 Testing {len(pdf_paths)} concurrent PDF parsing requests")
        print("⏳ Sending concurrent requests...")

        async def single_request(pdf_path, request_id):
            start_time = time.time()

            # Read and encode PDF
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                total_pages = len(pdf_reader.pages)

            api_url = f"{self.client.base_url}/parse_pdf"
            payload = {
                "data": b64_pdf,
                "method": method
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    elapsed_time = time.time() - start_time

                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Failed to parse PDF: {pdf_path}"
                        )

                    _result = await response.json()

                    pages_per_second = total_pages / elapsed_time if elapsed_time > 0 else 0

                    return request_id, elapsed_time, total_pages, pages_per_second, pdf_path

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(path, i+1) for i, path in enumerate(pdf_paths)])
            total_time = time.time() - start_time
            return results, total_time

        results, total_time = asyncio.run(run_concurrent_requests())

        results.sort(key=lambda x: x[0])

        print("✅ All PDF parsing completed!")
        total_pages_processed = 0
        for request_id, elapsed_time, total_pages, pages_per_second, pdf_path in results:
            print(
                f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {total_pages} pages, 🔥 {pages_per_second:.2f} pages/sec")
            print(f"PDF: {pdf_path}")
            print("")
            total_pages_processed += total_pages

        print(
            f"📊 Average time per PDF: {sum(result[1] for result in results) / len(results):.2f}s")
        print(
            f"📊 Average pages per second per PDF: {sum(result[3] for result in results) / len(results):.2f}")
        print(
            f"📊 Overall pages per second: {total_pages_processed / total_time if total_time > 0 else 0:.2f}")
        print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
        print(f"📊 Total pages processed: {total_pages_processed}")
        print("")
