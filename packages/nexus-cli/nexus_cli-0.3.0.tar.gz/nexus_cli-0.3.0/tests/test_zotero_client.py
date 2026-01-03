"""Tests for ZoteroClient class."""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nexus.research.zotero import ZoteroClient, ZoteroItem


@pytest.fixture
def mock_zotero_db(temp_dir):
    """Create a mock Zotero database with test data."""
    db_path = temp_dir / "zotero.sqlite"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create necessary tables
    cursor.executescript(
        """
        CREATE TABLE itemTypes (
            itemTypeID INTEGER PRIMARY KEY,
            typeName TEXT
        );

        CREATE TABLE items (
            itemID INTEGER PRIMARY KEY,
            key TEXT UNIQUE,
            itemTypeID INTEGER,
            dateModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE itemData (
            itemID INTEGER,
            fieldID INTEGER,
            valueID INTEGER,
            PRIMARY KEY (itemID, fieldID)
        );

        CREATE TABLE itemDataValues (
            valueID INTEGER PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE creators (
            creatorID INTEGER PRIMARY KEY,
            firstName TEXT,
            lastName TEXT
        );

        CREATE TABLE creatorTypes (
            creatorTypeID INTEGER PRIMARY KEY,
            creatorType TEXT
        );

        CREATE TABLE itemCreators (
            itemID INTEGER,
            creatorID INTEGER,
            creatorTypeID INTEGER,
            orderIndex INTEGER,
            PRIMARY KEY (itemID, creatorID, creatorTypeID)
        );

        CREATE TABLE tags (
            tagID INTEGER PRIMARY KEY,
            name TEXT
        );

        CREATE TABLE itemTags (
            itemID INTEGER,
            tagID INTEGER,
            PRIMARY KEY (itemID, tagID)
        );

        CREATE TABLE collections (
            collectionID INTEGER PRIMARY KEY,
            collectionName TEXT
        );

        CREATE TABLE collectionItems (
            collectionID INTEGER,
            itemID INTEGER,
            PRIMARY KEY (collectionID, itemID)
        );

        -- Insert item types
        INSERT INTO itemTypes VALUES (1, 'journalArticle');
        INSERT INTO itemTypes VALUES (2, 'book');
        INSERT INTO itemTypes VALUES (3, 'attachment');

        -- Insert creator types
        INSERT INTO creatorTypes VALUES (1, 'author');

        -- Insert test items
        INSERT INTO items VALUES (1, 'ABCD1234', 1, CURRENT_TIMESTAMP);
        INSERT INTO items VALUES (2, 'EFGH5678', 2, CURRENT_TIMESTAMP);
        INSERT INTO items VALUES (3, 'ATTACH99', 3, CURRENT_TIMESTAMP);

        -- Insert field values (FIELD_TITLE=1, FIELD_ABSTRACT=2, FIELD_DATE=6)
        INSERT INTO itemDataValues VALUES (1, 'Mediation Analysis in Psychology');
        INSERT INTO itemDataValues VALUES (2, 'This is an abstract about mediation.');
        INSERT INTO itemDataValues VALUES (3, '2024');
        INSERT INTO itemDataValues VALUES (4, 'Statistics Textbook');
        INSERT INTO itemDataValues VALUES (5, 'A comprehensive statistics book.');
        INSERT INTO itemDataValues VALUES (6, '2023');

        INSERT INTO itemData VALUES (1, 1, 1);  -- Item 1 title
        INSERT INTO itemData VALUES (1, 2, 2);  -- Item 1 abstract
        INSERT INTO itemData VALUES (1, 6, 3);  -- Item 1 date
        INSERT INTO itemData VALUES (2, 1, 4);  -- Item 2 title
        INSERT INTO itemData VALUES (2, 2, 5);  -- Item 2 abstract
        INSERT INTO itemData VALUES (2, 6, 6);  -- Item 2 date

        -- Insert creators
        INSERT INTO creators VALUES (1, 'John', 'Smith');
        INSERT INTO creators VALUES (2, 'Mary', 'Jones');

        INSERT INTO itemCreators VALUES (1, 1, 1, 0);  -- Smith is author of item 1
        INSERT INTO itemCreators VALUES (1, 2, 1, 1);  -- Jones is also author
        INSERT INTO itemCreators VALUES (2, 1, 1, 0);  -- Smith is author of item 2

        -- Insert tags
        INSERT INTO tags VALUES (1, 'mediation');
        INSERT INTO tags VALUES (2, 'statistics');

        INSERT INTO itemTags VALUES (1, 1);  -- Item 1 has 'mediation' tag
        INSERT INTO itemTags VALUES (1, 2);  -- Item 1 has 'statistics' tag
        INSERT INTO itemTags VALUES (2, 2);  -- Item 2 has 'statistics' tag

        -- Insert collections
        INSERT INTO collections VALUES (1, 'Methods Papers');
        INSERT INTO collections VALUES (2, 'Textbooks');

        INSERT INTO collectionItems VALUES (1, 1);  -- Item 1 in Methods Papers
        INSERT INTO collectionItems VALUES (2, 2);  -- Item 2 in Textbooks
    """
    )

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def zotero_client(mock_zotero_db):
    """Create a ZoteroClient with test database."""
    return ZoteroClient(mock_zotero_db)


class TestZoteroClientBasics:
    """Test basic ZoteroClient functionality."""

    def test_exists_with_valid_db(self, zotero_client):
        """Test exists() with valid database."""
        assert zotero_client.exists() is True

    def test_exists_with_invalid_db(self, temp_dir):
        """Test exists() with nonexistent database."""
        client = ZoteroClient(temp_dir / "nonexistent.sqlite")
        assert client.exists() is False

    def test_count(self, zotero_client):
        """Test counting items (excluding attachments)."""
        count = zotero_client.count()
        assert count == 2  # Should not include attachments

    def test_count_nonexistent_db(self, temp_dir):
        """Test count with nonexistent database."""
        client = ZoteroClient(temp_dir / "nonexistent.sqlite")
        assert client.count() == 0


class TestZoteroSearch:
    """Test search functionality."""

    def test_search_by_title(self, zotero_client):
        """Test searching by title."""
        results = zotero_client.search("Mediation", limit=10)

        assert len(results) >= 1
        assert any("Mediation" in item.title for item in results)

    def test_search_by_abstract(self, zotero_client):
        """Test searching by abstract content."""
        results = zotero_client.search("comprehensive", limit=10)

        assert len(results) >= 1

    def test_search_by_author(self, zotero_client):
        """Test searching by author name."""
        results = zotero_client.search("Smith", limit=10)

        assert len(results) >= 1

    def test_search_limit(self, zotero_client):
        """Test search respects limit."""
        results = zotero_client.search("", limit=1)  # Empty query matches all

        # May or may not have results depending on implementation
        assert len(results) <= 1

    def test_search_by_item_type(self, zotero_client):
        """Test filtering by item type."""
        results = zotero_client.search("", item_type="book", limit=10)

        for item in results:
            assert item.item_type == "book"

    def test_search_by_tag(self, zotero_client):
        """Test filtering by tag."""
        results = zotero_client.search("", tag="mediation", limit=10)

        for item in results:
            assert "mediation" in [t.lower() for t in item.tags]

    def test_search_nonexistent_db(self, temp_dir):
        """Test search with nonexistent database."""
        client = ZoteroClient(temp_dir / "nonexistent.sqlite")
        results = client.search("test")

        assert results == []


class TestZoteroGet:
    """Test getting specific items."""

    def test_get_by_key(self, zotero_client):
        """Test getting item by key."""
        item = zotero_client.get("ABCD1234")

        assert item is not None
        assert item.key == "ABCD1234"
        assert "Mediation" in item.title

    def test_get_invalid_key(self, zotero_client):
        """Test getting item with invalid key."""
        item = zotero_client.get("INVALID")

        assert item is None

    def test_get_nonexistent_db(self, temp_dir):
        """Test get with nonexistent database."""
        client = ZoteroClient(temp_dir / "nonexistent.sqlite")
        item = client.get("ABC")

        assert item is None


class TestZoteroRecent:
    """Test recent items functionality."""

    def test_recent_items(self, zotero_client):
        """Test getting recent items."""
        items = zotero_client.recent(limit=10)

        assert len(items) >= 1
        assert len(items) <= 10

    def test_recent_excludes_attachments(self, zotero_client):
        """Test that recent excludes attachments."""
        items = zotero_client.recent(limit=10)

        for item in items:
            assert item.item_type != "attachment"

    def test_recent_limit(self, zotero_client):
        """Test recent respects limit."""
        items = zotero_client.recent(limit=1)

        assert len(items) <= 1

    def test_recent_nonexistent_db(self, temp_dir):
        """Test recent with nonexistent database."""
        client = ZoteroClient(temp_dir / "nonexistent.sqlite")
        items = client.recent()

        assert items == []


class TestZoteroItemBuilding:
    """Test item building and data extraction."""

    def test_item_has_authors(self, zotero_client):
        """Test that items have authors populated."""
        item = zotero_client.get("ABCD1234")

        assert item is not None
        assert len(item.authors) >= 1
        assert any("Smith" in author for author in item.authors)

    def test_item_has_tags(self, zotero_client):
        """Test that items have tags populated."""
        item = zotero_client.get("ABCD1234")

        assert item is not None
        assert len(item.tags) >= 1
        assert "mediation" in item.tags

    def test_item_has_collections(self, zotero_client):
        """Test that items have collections populated."""
        item = zotero_client.get("ABCD1234")

        assert item is not None
        assert len(item.collections) >= 1
        assert "Methods Papers" in item.collections

    def test_item_date(self, zotero_client):
        """Test that items have date populated."""
        item = zotero_client.get("ABCD1234")

        assert item is not None
        assert item.date == "2024"


class TestZoteroItemCitations:
    """Test citation generation (additional to existing tests)."""

    def test_citation_apa_three_to_five_authors(self):
        """Test APA citation with 3-5 authors."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="article",
            title="Test",
            authors=["Smith, J.", "Jones, M.", "Brown, P."],
            date="2024",
        )

        citation = item.citation_apa()
        assert "Smith, J., Jones, M., & Brown, P." in citation

    def test_citation_bibtex_book_type(self):
        """Test BibTeX for book type."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="book",
            title="Test Book",
            authors=["Author, A."],
            date="2024",
        )

        bibtex = item.citation_bibtex()
        assert "@book{" in bibtex

    def test_citation_bibtex_conference_paper(self):
        """Test BibTeX for conference paper."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="conferencePaper",
            title="Conference Paper",
            authors=["Author, A."],
            date="2024",
        )

        bibtex = item.citation_bibtex()
        assert "@inproceedings{" in bibtex

    def test_citation_bibtex_with_url(self):
        """Test BibTeX includes URL when present."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="article",
            title="Test",
            authors=["Smith, J."],
            date="2024",
            url="https://example.com/paper",
        )

        bibtex = item.citation_bibtex()
        assert "url = {https://example.com/paper}" in bibtex


class TestZoteroItemToDict:
    """Test item serialization."""

    def test_to_dict_truncates_abstract(self):
        """Test that to_dict truncates long abstracts."""
        long_abstract = "x" * 500
        item = ZoteroItem(
            item_id=1, key="TEST", item_type="article", title="Test", abstract=long_abstract
        )

        result = item.to_dict()

        assert len(result["abstract"]) <= 203  # 200 + "..."
        assert result["abstract"].endswith("...")

    def test_to_dict_all_fields(self):
        """Test to_dict includes all fields."""
        item = ZoteroItem(
            item_id=1,
            key="ABC123",
            item_type="journalArticle",
            title="Test Article",
            authors=["Smith, J."],
            date="2024",
            abstract="Test abstract",
            doi="10.1234/test",
            url="https://example.com",
            tags=["tag1"],
            collections=["col1"],
        )

        result = item.to_dict()

        assert result["item_id"] == 1
        assert result["key"] == "ABC123"
        assert result["item_type"] == "journalArticle"
        assert result["title"] == "Test Article"
        assert result["authors"] == ["Smith, J."]
        assert result["date"] == "2024"
        assert result["doi"] == "10.1234/test"
        assert result["url"] == "https://example.com"
        assert result["tags"] == ["tag1"]
        assert result["collections"] == ["col1"]
