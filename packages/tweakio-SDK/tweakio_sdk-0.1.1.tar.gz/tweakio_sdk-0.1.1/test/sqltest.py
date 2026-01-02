import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Fix path to include SDK root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Shared_Resources to avoid import errors (colorlog, etc)
mock_sr = MagicMock()
mock_logger = MagicMock()
mock_sr.logger = mock_logger
sys.modules["Shared_Resources"] = mock_sr

from Storage import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_tweakio.db"
        self.storage = Storage(self.test_db)
        
    def tearDown(self):
        self.storage.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists(self.test_db + "-wal"):
            os.remove(self.test_db + "-wal")
        if os.path.exists(self.test_db + "-shm"):
            os.remove(self.test_db + "-shm")

    def test_insert_and_retrieve(self):
        data = {
            "data_id": "msg_123",
            "chat": "Rohit",
            "message": "Hello World",
            "sender": "Rohit",
            "time": "10:00 AM"
        }
        
        # Test Insert
        result = self.storage.insert_message(data)
        self.assertTrue(result, "First insert should return True")
        
        # Test Duplicate Insert
        result_dup = self.storage.insert_message(data)
        self.assertFalse(result_dup, "Duplicate insert should return False")
        
        # Test Exists
        exists = self.storage.message_exists("msg_123")
        self.assertTrue(exists, "Message should exist")
        
        # Test Not Exists
        exists_fake = self.storage.message_exists("fake_id")
        self.assertFalse(exists_fake, "Fake ID should not exist")
        
        # Test Retrieve
        all_msgs = self.storage.get_all_messages()
        self.assertEqual(len(all_msgs), 1)
        self.assertEqual(all_msgs[0]['message'], "Hello World")
        print("✅ Storage tests passed!")

if __name__ == "__main__":
    unittest.main()
