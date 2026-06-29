from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone
import openpyxl

from imports.models import ImportBatch, LeadTimeRecord
from imports.services.import_validation_service import EXPECTED_HEADERS_A_TO_AH
from imports.services.lead_time_calculation_service import calculate_lead_times
from imports.services.lead_time_import_service import LeadTimeImportService


class LeadTimeImportTests(TestCase):
    def tearDown(self):
        for file_path in getattr(self, "temporary_files", []):
            Path(file_path).unlink(missing_ok=True)

    def test_missing_file_creates_file_not_found_batch(self):
        batch = LeadTimeImportService().import_file("data/missing.xlsx")

        self.assertEqual(batch.status, ImportBatch.Status.FILE_NOT_FOUND)
        self.assertEqual(ImportBatch.objects.count(), 1)
        self.assertEqual(LeadTimeRecord.objects.count(), 0)

    def test_missing_required_column_creates_validation_error_batch(self):
        file_path = self._create_workbook(headers=EXPECTED_HEADERS_A_TO_AH[:-1])

        batch = LeadTimeImportService().import_file(file_path)

        self.assertEqual(batch.status, ImportBatch.Status.VALIDATION_ERROR)
        self.assertIn("Cabeçalho", batch.error_message)
        self.assertEqual(LeadTimeRecord.objects.count(), 0)

    def test_valid_import_creates_success_batch_and_records(self):
        file_path = self._create_workbook()

        batch = LeadTimeImportService().import_file(file_path)

        self.assertEqual(batch.status, ImportBatch.Status.SUCCESS)
        self.assertEqual(batch.total_rows, 1)
        self.assertEqual(batch.valid_rows, 1)
        self.assertEqual(batch.invalid_rows, 0)

        record = LeadTimeRecord.objects.get()
        self.assertEqual(record.business_unit, "TABACO")
        self.assertEqual(record.invoice_number, "319554")
        self.assertEqual(record.vehicle_plate, "AZP8G94")
        self.assertEqual(record.invoice_value, Decimal("1674.40"))
        self.assertEqual(record.region, "")
        self.assertEqual(record.frequency, "")
        self.assertIsNotNone(record.operational_lead_time_hours)
        self.assertIsNotNone(record.carrier_lead_time_hours)

    def test_valid_import_reads_optional_region_and_frequency_headers(self):
        headers = EXPECTED_HEADERS_A_TO_AH + ["Regiao", "Frequencia"]
        row = self._valid_row() + ["SUL", "DIARIA"]
        file_path = self._create_workbook(headers=headers, row=row)

        batch = LeadTimeImportService().import_file(file_path)

        self.assertEqual(batch.status, ImportBatch.Status.SUCCESS)
        record = LeadTimeRecord.objects.get()
        self.assertEqual(record.region, "SUL")
        self.assertEqual(record.frequency, "DIARIA")

    def test_optional_region_and_frequency_values_are_normalized_as_text(self):
        headers = EXPECTED_HEADERS_A_TO_AH + ["REGIAO", "FREQ"]
        row = self._valid_row() + [123, 2]
        file_path = self._create_workbook(headers=headers, row=row)

        batch = LeadTimeImportService().import_file(file_path)

        self.assertEqual(batch.status, ImportBatch.Status.SUCCESS)
        record = LeadTimeRecord.objects.get()
        self.assertEqual(record.region, "123")
        self.assertEqual(record.frequency, "2")

    def test_model_has_optional_region_and_frequency_fields(self):
        region_field = LeadTimeRecord._meta.get_field("region")
        frequency_field = LeadTimeRecord._meta.get_field("frequency")

        self.assertEqual(region_field.max_length, 80)
        self.assertTrue(region_field.blank)
        self.assertTrue(region_field.db_index)
        self.assertEqual(frequency_field.max_length, 80)
        self.assertTrue(frequency_field.blank)
        self.assertTrue(frequency_field.db_index)

    def test_duplicate_file_creates_duplicated_batch_without_new_records(self):
        file_path = self._create_workbook()

        first_batch = LeadTimeImportService().import_file(file_path)
        second_batch = LeadTimeImportService().import_file(file_path)

        self.assertEqual(first_batch.status, ImportBatch.Status.SUCCESS)
        self.assertEqual(second_batch.status, ImportBatch.Status.DUPLICATED)
        self.assertEqual(LeadTimeRecord.objects.count(), 1)

    def test_command_rejects_non_local_source_mode(self):
        with self.assertRaises(CommandError):
            call_command("import_lead_time_records", source_mode="sftp")

    def test_lead_time_late_flags(self):
        current_timezone = timezone.get_current_timezone()
        invoice_issue = timezone.make_aware(
            datetime(2026, 5, 1, 0, 0),
            current_timezone,
        )
        load_datetime = timezone.make_aware(
            datetime(2026, 5, 5, 0, 0),
            current_timezone,
        )
        delivery_datetime = timezone.make_aware(
            datetime(2026, 5, 6, 1, 0),
            current_timezone,
        )

        result = calculate_lead_times(
            invoice_issue,
            load_datetime,
            delivery_datetime,
        )

        self.assertTrue(result["is_operational_late"])
        self.assertTrue(result["is_carrier_late"])

    def _create_workbook(self, headers=None, row=None):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "COM 001"
        worksheet.append(headers or EXPECTED_HEADERS_A_TO_AH)
        worksheet.append(row or self._valid_row())
        worksheet.append([None] * len(headers or EXPECTED_HEADERS_A_TO_AH))

        temporary_file = NamedTemporaryFile(
            suffix="Acompanhamento Lead Time - Tabaco mes de Maio 2026.xlsx",
            delete=False,
        )
        temporary_file.close()
        workbook.save(temporary_file.name)
        self.temporary_files = getattr(self, "temporary_files", [])
        self.temporary_files.append(temporary_file.name)
        return temporary_file.name

    def _valid_row(self):
        return [
            "04/05/26",
            470939,
            "948 TAINARA CAMARGO MONTE",
            "RT030",
            18,
            151.67,
            0.64,
            375.10,
            "AZP8G94",
            395,
            "BEATRIZ GOMES",
            None,
            None,
            "CARREGADO EM",
            datetime(2026, 5, 5),
            319554,
            11,
            datetime(2026, 5, 4),
            807679,
            6248888,
            "CLIENTE TESTE LTDA",
            "PONTA GROSSA",
            1674.40,
            "AZP8G94",
            "Ativa",
            "Entregue",
            None,
            "ENTREGUE",
            datetime(2026, 5, 5),
            time(16, 12),
            "UMOV",
            None,
            681,
            1,
        ]
