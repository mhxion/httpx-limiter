# Copyright (c) 2025 Moritz E. Beber
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


"""Test httpx-limiter's compatibility with Pyodide."""
from pytest_pyodide import run_in_pyodide
from pytest_pyodide.decorator import copy_files_to_pyodide


@run_in_pyodide
def test_python_in_pyodide(selenium):
    import sys

    assert sys.platform == "emscripten"


@copy_files_to_pyodide(
    file_list=[("dist/", "dist/")], install_wheels=True, recurse_directories=False
)
@run_in_pyodide(packages=["ssl", "micropip"])
async def test_imports(selenium_standalone):
    import micropip
    await micropip.install(["httpx~=0.25", "aiolimiter~=1.2"])

    import httpx
    from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter


@copy_files_to_pyodide(
    file_list=[("dist/", "dist/")], install_wheels=True, recurse_directories=False
)
@run_in_pyodide(packages=["ssl", "micropip"])
async def test_status(selenium_standalone):
    import micropip

    await micropip.install(["httpx~=0.25", "aiolimiter~=1.2"])
    # Passing the offline .whl path to micropip.install does not work.
    # But a remote path to .whl does!

    import httpx
    from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter
    from httpx_limiter import AsyncRateLimitedTransport, Rate

    limiter = AiolimiterAsyncLimiter.create(Rate.create(magnitude=10, duration=1))
    async with httpx.AsyncClient(transport=AsyncRateLimitedTransport.create(limiter=limiter)) as client:
        response = await client.get("https://httpbin.org/status/200")
        assert response.status_code == 200
