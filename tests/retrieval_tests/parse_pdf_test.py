"""Kolosal Server PDF Parsing Test with Enhanced Logging"""
import io
import os
import json
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
                       method: Optional[str] = "fast") -> bool:
        """Test parsing a PDF file with comprehensive logging."""
        # Log test start
        self.log_test_start("PDF Parsing Test", f"Testing file: {path}")
        
        # Status Report
        print(f"🚀 Testing PDF parsing: {path}")
        print("⏳ Sending request...")

        try:
            initial_time = time.time()

            # Check if file exists, create minimal PDF if not (following api_test.py pattern)
            if not os.path.exists(path):
                print(f"⚠️  Test file {path} not found, using minimal PDF content")
                # Use minimal PDF from api_test.py reference
                minimal_pdf_b64 = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoyMCA3MjAgVGQKKEhlbGxvIFdvcmxkKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NiAwMDAwMCBuIAowMDAwMDAwMTI0IDAwMDAwIG4gCjAwMDAwMDAyNzEgMDAwMDAgbiAKMDAwMDAwMDMzOCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQzMwolJUVPRgo="
                b64_pdf = minimal_pdf_b64
                total_pages = 1
            else:
                # Open the PDF file and send it to the Kolosal Server for parsing
                with open(path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                    total_pages = len(pdf_reader.pages)
                    b64_pdf = base64.b64encode(pdf_bytes).decode()

            # Send the PDF to the Kolosal Server for parsing with logging
            payload = {
                "data": b64_pdf,
                "method": method
            }

            response = self.make_tracked_request(
                test_name=f"PDF Parsing - {path}",
                method="POST",
                endpoint="/parse-pdf",
                json_data=payload,
                timeout=30,
                metadata={
                    "file_path": path,
                    "total_pages": total_pages,
                    "file_size_bytes": len(base64.b64decode(b64_pdf)),
                    "method": method
                }
            )
            elapsed_time = time.time() - initial_time

            # Validate response (following api_test.py pattern)
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('data', {}).get('extracted_text', '')
                pages_per_second = total_pages / elapsed_time if elapsed_time > 0 else 0
                
                print(f"✅ PDF parsing test: PASS - Extracted {len(extracted_text)} characters")
                print(f"📄 Total pages: {total_pages}")
                print(f"⏱️ Time per PDF: {elapsed_time:.2f} seconds")
                print(f"🔥 Pages per second: {pages_per_second:.2f}")
                print("")
                
                # Log test completion
                self.log_test_end("PDF Parsing Test", {
                    "total_pages": total_pages,
                    "elapsed_time": elapsed_time,
                    "pages_per_second": pages_per_second,
                    "method": method,
                    "extracted_length": len(extracted_text)
                })
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"❌ PDF parsing test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    print(f"❌ PDF parsing test: FAIL - HTTP {response.status_code}: {response.text}")
                print("")
                return False

        except Exception as e:
            print(f"❌ PDF parsing test: FAIL - {str(e)}")
            print("")
            return False

    def concurrent_parse_pdf(self,
                             pdf_paths: Optional[List[str]] = None,
                             method: Optional[str] = "fast") -> bool:
        """Test concurrent PDF parsing requests using asyncio with comprehensive logging."""
        # Log test start
        self.log_test_start("Concurrent PDF Parsing Test", f"Method: {method}")

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
        
        # Log request details
        request_config = {
            "concurrent_requests": len(pdf_paths),
            "method": method,
            "file_paths": [os.path.basename(path) for path in pdf_paths]
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

        async def single_request(pdf_path, request_id):
            start_time = time.time()

            # Read and encode PDF
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                total_pages = len(pdf_reader.pages)

            api_url = f"{self.client.base_url}/parse-pdf"
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

        try:
            results, total_time = asyncio.run(run_concurrent_requests())

            results.sort(key=lambda x: x[0])
            
            # Log response summary
            response_summary = {
                "total_requests": len(pdf_paths),
                "total_time": total_time,
                "results": [
                    {
                        "request_id": result[0],
                        "elapsed_time": result[1],
                        "total_pages": result[2],
                        "pages_per_second": result[3],
                        "file_name": os.path.basename(result[4])
                    } for result in results
                ]
            }
            print(f"📥 Concurrent requests summary: {json.dumps(response_summary, indent=2)}")

            print("✅ All PDF parsing completed!")
            total_pages_processed = 0
            successful_requests = 0
            
            for request_id, elapsed_time, total_pages, pages_per_second, pdf_path in results:
                print(
                    f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {total_pages} pages, 🔥 {pages_per_second:.2f} pages/sec")
                print(f"PDF: {pdf_path}")
                print("")
                total_pages_processed += total_pages
                successful_requests += 1

            avg_time = sum(result[1] for result in results) / len(results)
            avg_pages_per_sec = sum(result[3] for result in results) / len(results)
            overall_pages_per_sec = total_pages_processed / total_time if total_time > 0 else 0

            print(
                f"📊 Average time per PDF: {avg_time:.2f}s")
            print(
                f"📊 Average pages per second per PDF: {avg_pages_per_sec:.2f}")
            print(
                f"📊 Overall pages per second: {overall_pages_per_sec:.2f}")
            print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
            print(f"📊 Total pages processed: {total_pages_processed}")
            print(f"📊 Successful requests: {successful_requests}/{len(pdf_paths)}")
            print("")
            
            # Log test completion
            success_rate = successful_requests / len(pdf_paths)
            self.log_test_end("Concurrent PDF Parsing Test", {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "total_requests": len(pdf_paths),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "total_pages_processed": total_pages_processed,
                "method": method
            })
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Concurrent PDF parsing test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Concurrent PDF Parsing Test", {
                "success": False,
                "error": str(e),
                "method": method
            })
            return False
