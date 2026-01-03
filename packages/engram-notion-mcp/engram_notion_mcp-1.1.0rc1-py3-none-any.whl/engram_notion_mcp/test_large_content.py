import pytest
from unittest.mock import MagicMock, patch
import os
from engram_notion_mcp.server import create_page, update_page, notion

# Set dummy env var for tests
os.environ["NOTION_API_KEY"] = "secret_test"
os.environ["NOTION_PAGE_ID"] = "test-page-id"

def test_create_page_large_content_chunking():
    """
    Test that create_page automatically chunks content larger than 2000 characters.
    """
    # Create a string larger than 2000 characters
    long_content = "a" * 3000
    
    with patch.object(notion.pages, "create") as mock_create:
        mock_create.return_value = {"url": "http://notion.so/new-page"}
        
        create_page(title="Large Page", content=long_content, parent_id="parent-id")
        
        # Verify call arguments
        args, kwargs = mock_create.call_args
        children = kwargs.get("children", [])
        
        # Expectation: Content should be split into multiple blocks
        # Current implementation sends 1 block -> Test should FAIL
        assert len(children) > 1, f"Expected multiple blocks for {len(long_content)} chars, got {len(children)}"
        
        # Verify total content length is preserved (approximate check if we add newlines)
        total_chars = 0
        for block in children:
            text = block["paragraph"]["rich_text"][0]["text"]["content"]
            total_chars += len(text)
            assert len(text) <= 2000, "Individual block exceeded 2000 characters"
            
        assert total_chars >= 3000

def test_update_page_large_content_chunking():
    """
    Test that update_page automatically chunks content larger than 2000 characters.
    """
    long_content = "b" * 3000
    
    with patch.object(notion.blocks.children, "append") as mock_append:
        mock_append.return_value = {}
        
        update_page(page_id="page-id", title="Large Update", content=long_content)
        
        args, kwargs = mock_append.call_args
        children = kwargs.get("children", [])
        
        # First block is the heading, subsequent blocks should be the content
        content_blocks = [b for b in children if b["type"] == "paragraph"]
        
        # Expectation: multiple content blocks
        assert len(content_blocks) > 1, f"Expected multiple paragraph blocks, got {len(content_blocks)}"
        
        for block in content_blocks:
            text = block["paragraph"]["rich_text"][0]["text"]["content"]
            assert len(text) <= 2000, "Individual block exceeded 2000 characters"
