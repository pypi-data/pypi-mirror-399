import pytest
from unittest.mock import MagicMock, patch
import json
import os
from engram_notion_mcp.server import (
    remember_fact, 
    read_page_content, 
    list_databases, 
    send_alert, 
    search_memory,
    get_recent_memories,
    query_database,
    delete_block,
    notion
)

# Set dummy env var for tests
os.environ["NOTION_API_KEY"] = "secret_test"
os.environ["NOTION_PAGE_ID"] = "test-page-id"

def test_remember_fact():
    with patch("engram_notion_mcp.server._save_to_db") as mock_save:
        result = remember_fact(fact="Python is cool")
        assert "Remembered: Python is cool" in result
        mock_save.assert_called_once()

def test_read_page_content():
    with patch.object(notion.blocks.children, "list") as mock_list:
        mock_list.return_value = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "Hello Python"}]}
                }
            ]
        }
        
        result = read_page_content(page_id="test-id")
        assert "Hello Python" in result

def test_list_databases():
    with patch.object(notion, "search") as mock_search:
        mock_search.return_value = {
            "results": [
                {
                    "object": "database",
                    "id": "db-123",
                    "title": [{"plain_text": "Python DB"}]
                }
            ]
        }
        
        result = list_databases()
        assert "Python DB" in result
        assert "db-123" in result

def test_send_alert():
    with patch("httpx.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ["TELEGRAM_CHAT_ID"] = "chat"
        
        result = send_alert(message="Alert Python")
        assert "Alert sent successfully" in result

def test_search_memory():
    with patch("sqlite3.connect") as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [
            ("Ashwatthama story", '{"timestamp": "2025-12-30"}')
        ]
        
        result = search_memory(query="Ashwatthama")
        assert "Ashwatthama story" in result
        assert "2025-12-30" in result

def test_get_recent_memories():
    with patch("sqlite3.connect") as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [
            ("Recent fact", '{"type": "manual_fact"}')
        ]
        
        result = get_recent_memories(limit=1)
        assert "Recent fact" in result
        assert "[MANUAL_FACT]" in result

def test_query_database():
    # Use create=True because DatabasesEndpoint might not have query attribute 
    # until it's actually called (dynamic proxy)
    with patch.object(notion.databases, "query", create=True) as mock_query:
        mock_query.return_value = {
            "results": [
                {
                    "id": "page-123",
                    "properties": {
                        "Name": {"id": "title", "type": "title", "title": [{"plain_text": "Test Page"}]}
                    }
                }
            ]
        }
        
        result = query_database(database_id="db-123")
        assert "Test Page" in result
        assert "page-123" in result

def test_delete_block():
    with patch.object(notion.blocks, "delete") as mock_delete:
        mock_delete.return_value = {}
        
        result = delete_block(block_id="block-123")
        assert "Successfully deleted block block-123" in result
