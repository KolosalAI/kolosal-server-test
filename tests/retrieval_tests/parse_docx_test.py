"""Kolosal Server DOCX Parsing Test (Simplified)"""
import base64
import time
import asyncio
from typing import Optional, List
import requests
import aiohttp
from tests.kolosal_tests import KolosalTestBase


class ParseDOCXTest(KolosalTestBase):
    """Test class for DOCX parsing functionality in Kolosal Server."""

    def test_parse_docx(self,
                        path: Optional[str] = "test_files/test_docx.docx",
                        method: Optional[str] = "fast") -> None:
        """Test parsing a DOCX file."""
        # Status Report
        print(f"🚀 Testing DOCX parsing: {path}")
        print("⏳ Sending request...")

        initial_time = time.time()

        # Open the DOCX file and send it to the Kolosal Server for parsing
        with open(path, "rb") as docx_file:
            docx_bytes = docx_file.read()
            file_size_kb = len(docx_bytes) / 1024
            b64_docx = base64.b64encode(docx_bytes).decode()

        # Send the DOCX to the Kolosal Server for parsing
        api_url = f"{self.client.base_url}/parse_docx"

        payload = {
            "data": b64_docx,
            "method": method
        }

        response = requests.post(api_url, json=payload, timeout=30)
        elapsed_time = time.time() - initial_time

        assert response.status_code == 200, "Failed to parse DOCX file."

        # Extract result from response
        _result = response.json()

        kb_per_second = file_size_kb / elapsed_time if elapsed_time > 0 else 0

        # Status Report
        print("✅ DOCX parsing completed!")
        print(f"📄 File size: {file_size_kb:.2f} KB")
        print(f"⏱️ Time per DOCX: {elapsed_time:.2f} seconds")
        print(f"🔥 KB per second: {kb_per_second:.2f}")
        print("")

    def concurrent_parse_docx(self,
                              docx_paths: Optional[List[str]] = None,
                              method: Optional[str] = "fast") -> None:
        """Test concurrent DOCX parsing requests using asyncio."""

        if docx_paths is None:
            docx_paths = [
                "test_files/test_docx.docx",
                "test_files/test_docx2.docx",
                "test_files/test_docx3.docx",
                "test_files/test_docx4.docx",
                "test_files/test_docx5.docx"
            ]

        print(
            f"🚀 Testing {len(docx_paths)} concurrent DOCX parsing requests")
        print("⏳ Sending concurrent requests...")

        async def single_request(docx_path, request_id):
            start_time = time.time()

            # Read and encode DOCX
            with open(docx_path, "rb") as docx_file:
                docx_bytes = docx_file.read()
                b64_docx = base64.b64encode(docx_bytes).decode()
                file_size_kb = len(docx_bytes) / 1024

            api_url = f"{self.client.base_url}/parse_docx"
            payload = {
                "data": b64_docx,
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
                            message=f"Failed to parse DOCX: {docx_path}"
                        )

                    _result = await response.json()

                    kb_per_second = file_size_kb / elapsed_time if elapsed_time > 0 else 0

                    return request_id, elapsed_time, file_size_kb, kb_per_second, docx_path

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(path, i+1) for i, path in enumerate(docx_paths)])
            total_time = time.time() - start_time
            return results, total_time

        results, total_time = asyncio.run(run_concurrent_requests())

        results.sort(key=lambda x: x[0])

        print("✅ All DOCX parsing completed!")
        total_kb_processed = 0
        for request_id, elapsed_time, file_size_kb, kb_per_second, docx_path in results:
            print(
                f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {file_size_kb:.2f} KB, 🔥 {kb_per_second:.2f} KB/sec")
            print(f"DOCX: {docx_path}")
            print("")
            total_kb_processed += file_size_kb

        print(
            f"📊 Average time per DOCX: {sum(result[1] for result in results) / len(results):.2f}s")
        print(
            f"📊 Average KB per second per DOCX: {sum(result[3] for result in results) / len(results):.2f}")
        print(
            f"📊 Overall KB per second: {total_kb_processed / total_time if total_time > 0 else 0:.2f}")
        print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
        print(f"📊 Total KB processed: {total_kb_processed:.2f}")
        print("")
