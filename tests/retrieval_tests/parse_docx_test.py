"""Kolosal Server DOCX Parsing Test with Enhanced Logging"""
import base64
import time
import asyncio
import json
import os
from typing import Optional, List
import requests
import aiohttp
from tests.kolosal_tests import KolosalTestBase


class ParseDOCXTest(KolosalTestBase):
    """Test class for DOCX parsing functionality in Kolosal Server."""

    def test_parse_docx(self,
                        path: Optional[str] = "test_files/test_docx.docx",
                        method: Optional[str] = "fast") -> None:
        """Test parsing a DOCX file with comprehensive logging."""
        import os
        
        # Convert to absolute path if relative
        if not os.path.isabs(path):
            # Get the project root directory (where test_files should be)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..")
            path = os.path.join(project_root, path)
            path = os.path.normpath(path)
        
        # Log test start
        self.log_test_start("DOCX Parsing Test", f"Testing file: {path}")
        
        # Check if file exists
        if not os.path.exists(path):
            print(f"❌ Test file not found: {path}")
            print(f"Current working directory: {os.getcwd()}")
            print("Looking for test_files directory...")
            
            # Search for test_files directory
            test_dirs = []
            for root, dirs, files in os.walk("."):
                if "test_files" in dirs:
                    test_dir = os.path.join(root, "test_files")
                    test_dirs.append(test_dir)
                    
            if test_dirs:
                print("Found test_files directories:")
                for test_dir in test_dirs:
                    print(f"  - {os.path.abspath(test_dir)}")
                    if os.path.exists(test_dir):
                        docx_files = [f for f in os.listdir(test_dir) if f.endswith('.docx')]
                        if docx_files:
                            print(f"    DOCX files: {docx_files}")
            
            raise FileNotFoundError(f"Test file not found: {path}")
        
        # Status Report
        print(f"🚀 Testing DOCX parsing: {path}")
        print("⏳ Sending request...")

        initial_time = time.time()

        try:
            # Open the DOCX file and send it to the Kolosal Server for parsing
            with open(path, "rb") as docx_file:
                docx_bytes = docx_file.read()
                file_size_kb = len(docx_bytes) / 1024
                b64_docx = base64.b64encode(docx_bytes).decode()
        except Exception as e:
            print(f"❌ Error reading file {path}: {str(e)}")
            raise

        # Send the DOCX to the Kolosal Server for parsing with logging
        payload = {
            "data": b64_docx,
            "method": method
        }

        try:
            response = self.make_tracked_request(
                test_name=f"DOCX Parsing - {path}",
                method="POST",
                endpoint="/parse-docx",
                json_data=payload,
                timeout=30,
                metadata={
                    "file_path": path,
                    "file_size_kb": file_size_kb,
                    "method": method
                }
            )
            elapsed_time = time.time() - initial_time
            
            if response.status_code != 200:
                print(f"❌ Server returned status code: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"Failed to parse DOCX file. Status: {response.status_code}")

            # Extract result from response
            try:
                _result = response.json()
            except Exception as e:
                print(f"❌ Failed to parse JSON response: {str(e)}")
                print(f"Response text: {response.text}")
                raise Exception(f"Invalid JSON response: {str(e)}")

        except requests.exceptions.Timeout:
            print("❌ Request timed out after 30 seconds")
            raise Exception("Request timeout")
        except requests.exceptions.ConnectionError:
            print("❌ Failed to connect to server")
            raise Exception("Connection error")
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            raise

        kb_per_second = file_size_kb / elapsed_time if elapsed_time > 0 else 0

        # Status Report
        print("✅ DOCX parsing completed!")
        print(f"📄 File size: {file_size_kb:.2f} KB")
        print(f"⏱️ Time per DOCX: {elapsed_time:.2f} seconds")
        print(f"🔥 KB per second: {kb_per_second:.2f}")
        print("")

    def concurrent_parse_docx(self,
                              docx_paths: Optional[List[str]] = None,
                              method: Optional[str] = "fast") -> bool:
        """Test concurrent DOCX parsing requests using asyncio with comprehensive logging."""
        import os
        
        # Log test start
        self.log_test_start("Concurrent DOCX Parsing Test", f"Method: {method}")

        if docx_paths is None:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..")
            project_root = os.path.normpath(project_root)
            
            # Check which files actually exist
            potential_files = [
                "test_files/test_docx.docx",
                "test_files/test_docx1.docx", 
                "test_files/test_docx2.docx",
                "test_files/test_docx3.docx",
                "test_files/test_docx4.docx",
                "test_files/test_docx5.docx"
            ]
            
            # Convert to absolute paths and check existence
            docx_paths = []
            for rel_path in potential_files:
                abs_path = os.path.join(project_root, rel_path)
                abs_path = os.path.normpath(abs_path)
                if os.path.exists(abs_path):
                    docx_paths.append(abs_path)
            
            if not docx_paths:
                print("❌ No DOCX test files found!")
                print(f"Searched in project root: {project_root}")
                
                # Search for test_files directory
                test_files_dir = os.path.join(project_root, "test_files")
                if os.path.exists(test_files_dir):
                    print("Available files in test_files directory:")
                    for file in os.listdir(test_files_dir):
                        if file.endswith('.docx'):
                            print(f"  - {file}")
                            docx_paths.append(os.path.join(test_files_dir, file))
                            
                if not docx_paths:
                    raise FileNotFoundError("No DOCX test files found")
        else:
            # Convert relative paths to absolute if needed
            abs_paths = []
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..")
            project_root = os.path.normpath(project_root)
            
            for path in docx_paths:
                if not os.path.isabs(path):
                    abs_path = os.path.join(project_root, path)
                    abs_path = os.path.normpath(abs_path)
                    abs_paths.append(abs_path)
                else:
                    abs_paths.append(path)
            docx_paths = abs_paths
        
        # Verify all files exist
        missing_files = [path for path in docx_paths if not os.path.exists(path)]
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            raise FileNotFoundError(f"Missing test files: {missing_files}")

        print(
            f"🚀 Testing {len(docx_paths)} concurrent DOCX parsing requests")
        print("⏳ Sending concurrent requests...")
        
        # Log request details
        request_config = {
            "concurrent_requests": len(docx_paths),
            "method": method,
            "file_paths": [os.path.basename(path) for path in docx_paths]
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

        async def single_request(docx_path, request_id):
            start_time = time.time()

            try:
                # Read and encode DOCX
                with open(docx_path, "rb") as docx_file:
                    docx_bytes = docx_file.read()
                    b64_docx = base64.b64encode(docx_bytes).decode()
                    file_size_kb = len(docx_bytes) / 1024
            except Exception as e:
                print(f"❌ Error reading file {docx_path}: {str(e)}")
                raise

            api_url = f"{self.client.base_url}/parse-docx"
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

        try:
            results, total_time = asyncio.run(run_concurrent_requests())

            results.sort(key=lambda x: x[0])
            
            # Log response summary
            response_summary = {
                "total_requests": len(docx_paths),
                "total_time": total_time,
                "results": [
                    {
                        "request_id": result[0],
                        "elapsed_time": result[1],
                        "file_size_kb": result[2],
                        "kb_per_second": result[3],
                        "file_name": os.path.basename(result[4])
                    } for result in results
                ]
            }
            print(f"📥 Concurrent requests summary: {json.dumps(response_summary, indent=2)}")

            print("✅ All DOCX parsing completed!")
            total_kb_processed = 0
            successful_requests = 0
            
            for request_id, elapsed_time, file_size_kb, kb_per_second, docx_path in results:
                print(
                    f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {file_size_kb:.2f} KB, 🔥 {kb_per_second:.2f} KB/sec")
                print(f"DOCX: {docx_path}")
                print("")
                total_kb_processed += file_size_kb
                successful_requests += 1

            avg_time = sum(result[1] for result in results) / len(results)
            avg_kb_per_sec = sum(result[3] for result in results) / len(results)
            overall_kb_per_sec = total_kb_processed / total_time if total_time > 0 else 0

            print(
                f"📊 Average time per DOCX: {avg_time:.2f}s")
            print(
                f"📊 Average KB per second per DOCX: {avg_kb_per_sec:.2f}")
            print(
                f"📊 Overall KB per second: {overall_kb_per_sec:.2f}")
            print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
            print(f"📊 Total KB processed: {total_kb_processed:.2f}")
            print(f"📊 Successful requests: {successful_requests}/{len(docx_paths)}")
            print("")
            
            # Log test completion
            success_rate = successful_requests / len(docx_paths)
            self.log_test_end("Concurrent DOCX Parsing Test", {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "total_requests": len(docx_paths),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "total_kb_processed": total_kb_processed,
                "method": method
            })
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Concurrent DOCX parsing test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Concurrent DOCX Parsing Test", {
                "success": False,
                "error": str(e),
                "method": method
            })
            return False
