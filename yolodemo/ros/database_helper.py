import sqlite3
from typing import List, Dict, Any

class DatabaseHelper:
    def __init__(self, db_path: str = "roscar.db"):
        self.db_path = self._get_db_path()
        self._ensure_table()

    def _get_db_path(self) -> str:
        from pathlib import Path
        documents = Path.home() / "Documents"
        db_dir = documents / "roscar"
        db_dir.mkdir(parents=True, exist_ok=True)
        return str(db_dir / "roscar.db")

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bucketNumber TEXT,
                temperature TEXT,
                oxygenLevel TEXT,
                phLevel TEXT,
                testTime TEXT,
                photoPath TEXT,
                photoResult TEXT
            )
        """)
        conn.commit()
        conn.close()


    def insert_data(self, data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO data (bucketNumber, temperature, oxygenLevel, phLevel, testTime, photoPath, photoResult)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            data["bucketNumber"],
            data["temperature"],
            data["oxygenLevel"],
            data["phLevel"],
            data["testTime"],
            data["photoPath"],
            data["photoResult"]
        ])
        conn.commit()
        conn.close()

    def get_latest_per_bucket(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, bucketNumber, temperature, oxygenLevel, phLevel, testTime, photoPath, photoResult
            FROM data
            WHERE testTime IN (
                SELECT MAX(testTime) FROM data GROUP BY bucketNumber
            )
            ORDER BY bucketNumber
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    def get_data_by_bucket(self, bucket_number: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM data WHERE bucketNumber = ? ORDER BY testTime DESC",
            (bucket_number,)
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    def delete_data(self, record_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

    def insert_initial_data(self):
        sample_data = [
            {
                "bucketNumber": "1号桶",
                "temperature": "罗非鱼",
                "oxygenLevel": "7.5 mg/L",
                "phLevel": "7.5",
                "testTime": "2024-12-10 08:00:00",
                "photoPath": "C:/Users/qihe/Desktop/Captured_Images/take_photo_20241226_173128.jpg",
                "photoResult": "清澈"
            },
            {
                "bucketNumber": "2号桶",
                "temperature": "虾",
                "oxygenLevel": "7.8 mg/L",
                "phLevel": "7.8",
                "testTime": "2024-12-10 08:30:00",
                "photoPath": "C:/Users/qihe/Desktop/Captured_Images/device_20241230_191807.jpg",
                "photoResult": "正常"
            },
            {
                "bucketNumber": "3号桶",
                "temperature": "三文鱼",
                "oxygenLevel": "7.2 mg/L",
                "phLevel": "7.2",
                "testTime": "2024-12-10 09:00:00",
                "photoPath": "C:/Users/qihe/Desktop/Captured_Images/device_20241226_203914.jpg",
                "photoResult": "正常"
            }
        ]

        for item in sample_data:
            self.insert_data(item)
