import os
import uuid
import time
import pytest
import asyncio
import polarion_rest_client as prc
from polarion_rest_client.client import PolarionClient, PolarionAsyncClient
from polarion_rest_client.workitem import WorkItem
from polarion_rest_client.error import Forbidden, Unauthorized

# --- Helpers ---

def _create_items_sync(wi, project_id, wi_type, count, token):
    ids = []
    for i in range(count):
        res = wi.create(project_id, wi_type=wi_type, title=f"Test List Sync {token} {i}")
        ids.append(res['id'])
    return ids

async def _create_items_async(wi, project_id, wi_type, count, token):
    tasks = [
        wi.create(project_id, wi_type=wi_type, title=f"Test List Async {token} {i}")
        for i in range(count)
    ]
    results = await asyncio.gather(*tasks)
    return [r['id'] for r in results]

def _cleanup_sync(wi, project_id, full_ids):
    if not full_ids:
        return
    short_ids = [fid.split("/")[-1] for fid in full_ids]
    try:
        wi.delete(project_id, short_ids)
    except Exception:
        pass

async def _cleanup_async(wi, project_id, full_ids):
    if not full_ids:
        return
    short_ids = [fid.split("/")[-1] for fid in full_ids]
    try:
        await wi.delete(project_id, short_ids)
    except Exception:
        pass

# --- Retry Logic ---

def _wait_for_list_sync(func, min_count, retries=30, delay=1.0):
    """Retry a sync list function until it returns at least min_count items."""
    last_res = []
    for _ in range(retries):
        last_res = func()
        if len(last_res) >= min_count:
            return last_res
        time.sleep(delay)
    return last_res

async def _wait_for_list_async(func, min_count, retries=30, delay=1.0):
    """Retry an async list function until it returns at least min_count items."""
    last_res = []
    for _ in range(retries):
        last_res = await func()
        if len(last_res) >= min_count:
            return last_res
        await asyncio.sleep(delay)
    return last_res

# --- Tests ---

@pytest.mark.integration
@pytest.mark.parametrize("mode", ["sync", "async"])
def test_workitem_list_pagination_and_fetchall(mode):
    """
    Test WorkItem.list() for:
    - Pagination (page 1, page 2)
    - Fetch all (page_size=-1)
    - Filtering via query
    """
    project_id = os.getenv("POLARION_TEST_PROJECT_ID")
    if not project_id:
        pytest.skip("Set POLARION_TEST_PROJECT_ID")
    wi_type = os.getenv("POLARION_TEST_WI_TYPE", "task")

    token = uuid.uuid4().hex[:6]
    item_count = 5

    # Run Sync
    if mode == "sync":
        try:
            pc = PolarionClient(**prc.get_env_vars())
        except Exception:
            pytest.skip("Env vars missing")
            return

        wi = WorkItem(pc)
        created_ids = []

        try:
            # Setup
            created_ids = _create_items_sync(wi, project_id, wi_type, item_count, token)

            # Wait for search index to catch up using the first page check
            def _get_page1():
                return wi.list(project_id, page_size=2, page_number=1, query=f'title:"{token}"')

            page1 = _wait_for_list_sync(_get_page1, 2)
            assert len(page1) == 2, "Failed to retrieve page 1 (index lag?)"

            # Test 2: Pagination - Page 2
            page2 = wi.list(project_id, page_size=2, page_number=2, query=f'title:"{token}"')
            assert len(page2) == 2
            # Ensure different items
            p1_ids = {x['id'] for x in page1}
            p2_ids = {x['id'] for x in page2}
            assert p1_ids.isdisjoint(p2_ids)

            # Test 3: Fetch All
            # Explicitly set chunk_size=50 to avoid server limits (often 100)
            def _get_all():
                return wi.list(project_id, page_size=-1, query=f'title:"{token}"', chunk_size=50)

            all_items = _wait_for_list_sync(_get_all, item_count)

            found_ids = {x['id'] for x in all_items}
            assert set(created_ids).issubset(found_ids), \
                f"Missing items. Created: {len(created_ids)}, Found: {len(found_ids)}"
            assert len(all_items) >= item_count

            # Test 4: Fields filtering
            partial = wi.list(project_id, page_size=1, query=f'title:"{token}"', fields=["id", "title"])
            assert len(partial) > 0
            attr = partial[0].get("attributes", {})
            assert "title" in attr

        except (Forbidden, Unauthorized) as e:
            pytest.skip(f"Permission error: {e}")
        finally:
            _cleanup_sync(wi, project_id, created_ids)

    # Run Async
    else:
        async def _run_async():
            try:
                pc = PolarionAsyncClient(**prc.get_env_vars())
            except Exception:
                pytest.skip("Env vars missing")
                return
            except RuntimeError:
                pytest.skip("Async client missing")
                return

            async with pc as client:
                wi = WorkItem(client)
                created_ids = []
                try:
                    # Setup
                    created_ids = await _create_items_async(wi, project_id, wi_type, item_count, token)

                    # Wait for search index using page 1
                    async def _get_page1():
                        return await wi.list(project_id, page_size=2, page_number=1, query=f'title:"{token}"')

                    page1 = await _wait_for_list_async(_get_page1, 2)
                    assert len(page1) == 2, "Failed to retrieve page 1 (index lag?)"

                    # Test 2: Pagination - Page 2
                    page2 = await wi.list(project_id, page_size=2, page_number=2, query=f'title:"{token}"')
                    assert len(page2) == 2
                    p1_ids = {x['id'] for x in page1}
                    p2_ids = {x['id'] for x in page2}
                    assert p1_ids.isdisjoint(p2_ids)

                    # Test 3: Fetch All
                    async def _get_all():
                        return await wi.list(project_id, page_size=-1, query=f'title:"{token}"', chunk_size=50)

                    all_items = await _wait_for_list_async(_get_all, item_count)

                    found_ids = {x['id'] for x in all_items}
                    assert set(created_ids).issubset(found_ids)
                    assert len(all_items) >= item_count

                    # Test 4: Fields filtering
                    partial = await wi.list(project_id, page_size=1, query=f'title:"{token}"', fields=["id", "title"])
                    assert len(partial) > 0
                    attr = partial[0].get("attributes", {})
                    assert "title" in attr

                except (Forbidden, Unauthorized) as e:
                    pytest.skip(f"Permission error: {e}")
                finally:
                    await _cleanup_async(wi, project_id, created_ids)

        asyncio.run(_run_async())
