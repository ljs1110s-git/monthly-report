import io
import os
import tempfile
import unittest

import app as reports_app


class ReportPeriodTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_folder = reports_app.app.config["UPLOAD_FOLDER"]
        reports_app.app.config["UPLOAD_FOLDER"] = self.directory.name
        self.client = reports_app.app.test_client()

    def tearDown(self):
        reports_app.app.config["UPLOAD_FOLDER"] = self.old_folder
        self.directory.cleanup()

    def upload(self, filename, year=2026, month=10):
        return self.client.post("/upload", data={
            "files": (io.BytesIO(b"%PDF-1.4\n"), filename),
            "year": str(year), "month": str(month),
        })

    def test_period_survives_requests_and_duplicate_filenames(self):
        self.assertEqual(self.upload("report.pdf").status_code, 302)
        self.assertEqual(self.upload("report.pdf", 2027, 1).status_code, 302)
        entries = {r["filename"]: r for r in self.client.get("/api/files").json["reports"]}
        self.assertEqual((entries["report.pdf"]["year"], entries["report.pdf"]["month"]), (2026, 10))
        self.assertEqual((entries["report_2.pdf"]["year"], entries["report_2.pdf"]["month"]), (2027, 1))
        with self.client.get("/uploads/report.pdf") as response:
            self.assertEqual(response.data, b"%PDF-1.4\n")

    def test_legacy_files_are_inferred_or_left_unclassified(self):
        for filename in ["보고서(제2026-10호).pdf", "2027년 2월.pdf", "unknown.pdf", "2026-13.pdf"]:
            with open(os.path.join(self.directory.name, filename), "wb") as report:
                report.write(b"%PDF-1.4\n")
        entries = {r["filename"]: r for r in self.client.get("/api/files").json["reports"]}
        self.assertEqual(entries["보고서(제2026-10호).pdf"]["month"], 10)
        self.assertEqual(entries["2027년 2월.pdf"]["year"], 2027)
        self.assertIsNone(entries["unknown.pdf"]["year"])
        self.assertIsNone(entries["2026-13.pdf"]["month"])

    def test_invalid_period_does_not_save_upload(self):
        for year, month in [(2025, 1), (2026, 13), (2026, 0), ("", 10)]:
            self.assertEqual(self.upload("report.pdf", year, month).status_code, 400)
        self.assertEqual(os.listdir(self.directory.name), [])

    def test_admin_can_correct_period_and_delete_metadata(self):
        self.upload("report.pdf")
        data = {"filename": "report.pdf", "year": 2027, "month": 3, "password": "incorrect"}
        self.assertEqual(self.client.post("/api/report-period", json=data).status_code, 403)
        data["password"] = reports_app.ADMIN_PASSWORD
        self.assertEqual(self.client.post("/api/report-period", json=data).status_code, 200)
        self.assertEqual(self.client.get("/api/files").json["reports"][0]["year"], 2027)
        self.assertEqual(self.client.post("/delete", json=data).status_code, 200)
        self.assertEqual(os.listdir(self.directory.name), [])


if __name__ == "__main__":
    unittest.main()
