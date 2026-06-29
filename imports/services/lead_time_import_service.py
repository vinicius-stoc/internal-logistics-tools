from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
import hashlib
import re

from django.db import transaction
from django.utils import timezone

from imports.models import ImportBatch, LeadTimeRecord

from .excel_reader_service import RowNormalizationError, read_lead_time_rows
from .file_hash_service import calculate_file_sha256
from .import_validation_service import EXPECTED_SHEET_NAME, ImportValidationError
from .lead_time_calculation_service import calculate_lead_times


BULK_CREATE_BATCH_SIZE = 1000


class LeadTimeImportService:
    def import_file(self, file_path, source_mode=ImportBatch.SourceMode.LOCAL):
        path = Path(file_path)
        if not path.exists():
            return self._create_file_not_found_batch(path, source_mode)

        file_hash = calculate_file_sha256(path)
        if ImportBatch.objects.filter(
            file_hash=file_hash,
            status=ImportBatch.Status.SUCCESS,
        ).exists():
            return ImportBatch.objects.create(
                source_mode=source_mode,
                file_name=path.name,
                file_path=str(path),
                file_hash=file_hash,
                sheet_name=EXPECTED_SHEET_NAME,
                status=ImportBatch.Status.DUPLICATED,
                started_at=timezone.now(),
                finished_at=timezone.now(),
                technical_details={
                    "reason": "Arquivo já importado com sucesso.",
                },
            )

        batch = ImportBatch.objects.create(
            source_mode=source_mode,
            file_name=path.name,
            file_path=str(path),
            file_hash=file_hash,
            sheet_name=EXPECTED_SHEET_NAME,
            status=ImportBatch.Status.PROCESSING,
            started_at=timezone.now(),
        )

        try:
            return self._process_batch(batch, path)
        except ImportValidationError as exc:
            return self._finish_with_error(
                batch,
                ImportBatch.Status.VALIDATION_ERROR,
                str(exc.args[0]),
                {"details": exc.args[1:] if len(exc.args) > 1 else []},
            )
        except Exception as exc:
            return self._finish_with_error(
                batch,
                ImportBatch.Status.ERROR,
                str(exc),
                {"error_type": exc.__class__.__name__},
            )

    def _process_batch(self, batch, path):
        business_unit = extract_business_unit_from_filename(path.name)
        records = []
        invalid_rows = []
        total_rows = 0

        for row_number, row, row_error in read_lead_time_rows(path):
            total_rows += 1
            if row_error:
                invalid_rows.append(
                    {
                        "row_number": row_number,
                        "error": str(row_error),
                    }
                )
                continue

            try:
                record = self._build_record(batch, row_number, row, business_unit)
            except RowNormalizationError as exc:
                invalid_rows.append(
                    {
                        "row_number": row_number,
                        "error": str(exc),
                    }
                )
                continue
            records.append(record)

        if not records:
            return self._finish_with_error(
                batch,
                ImportBatch.Status.VALIDATION_ERROR,
                "Nenhuma linha válida encontrada para importação.",
                {
                    "total_rows": total_rows,
                    "invalid_rows_sample": invalid_rows[:20],
                },
            )

        with transaction.atomic():
            LeadTimeRecord.objects.bulk_create(
                records,
                batch_size=BULK_CREATE_BATCH_SIZE,
            )

        batch.total_rows = total_rows
        batch.valid_rows = len(records)
        batch.invalid_rows = len(invalid_rows)
        batch.status = ImportBatch.Status.SUCCESS
        batch.finished_at = timezone.now()
        batch.technical_details = {
            "business_unit": business_unit,
            "invalid_rows_sample": invalid_rows[:20],
            "invalid_rows_sample_limited": len(invalid_rows) > 20,
            "import_rule": "COM 001 A:AH, descartando a segunda coluna Placa; region/frequency opcionais por cabecalho.",
        }
        batch.save(
            update_fields=[
                "total_rows",
                "valid_rows",
                "invalid_rows",
                "status",
                "finished_at",
                "technical_details",
                "updated_at",
            ]
        )
        return batch

    def _build_record(self, batch, row_number, row, business_unit):
        delivery_datetime = combine_date_and_time(
            row["customer_delivery_date"],
            row["customer_delivery_time"],
        )
        invoice_issue_datetime = combine_date_and_time(
            row["invoice_issue_date"],
            time.min,
        )
        load_datetime = combine_date_and_time(row["load_date"], time.min)
        lead_times = calculate_lead_times(
            invoice_issue_datetime,
            load_datetime,
            delivery_datetime,
        )

        row_hash = calculate_row_hash(row, business_unit)
        return LeadTimeRecord(
            import_batch=batch,
            row_number=row_number,
            row_hash=row_hash,
            business_unit=business_unit,
            customer_delivery_datetime=delivery_datetime,
            **row,
            **lead_times,
        )

    def _create_file_not_found_batch(self, path, source_mode):
        now = timezone.now()
        return ImportBatch.objects.create(
            source_mode=source_mode,
            file_name=path.name,
            file_path=str(path),
            file_hash="",
            sheet_name=EXPECTED_SHEET_NAME,
            status=ImportBatch.Status.FILE_NOT_FOUND,
            started_at=now,
            finished_at=now,
            error_message="Arquivo não encontrado.",
        )

    def _finish_with_error(self, batch, status, message, technical_details):
        batch.status = status
        batch.finished_at = timezone.now()
        batch.error_message = message
        batch.technical_details = technical_details
        batch.save(
            update_fields=[
                "status",
                "finished_at",
                "error_message",
                "technical_details",
                "updated_at",
            ]
        )
        return batch


def extract_business_unit_from_filename(file_name):
    match = re.search(r"Lead Time\s*-\s*(.*?)\s+mes\s+de", file_name, re.IGNORECASE)
    if match:
        return match.group(1).strip().upper()
    return Path(file_name).stem.strip().upper()


def combine_date_and_time(date_value, time_value):
    if not date_value:
        return None
    combined = datetime.combine(date_value, time_value or time.min)
    if timezone.is_naive(combined):
        return timezone.make_aware(combined, timezone.get_current_timezone())
    return combined


def calculate_row_hash(row, business_unit):
    values = [business_unit]
    for key in sorted(row):
        value = row[key]
        if isinstance(value, Decimal):
            value = str(value.normalize())
        values.append(f"{key}={value}")
    return hashlib.sha256("|".join(values).encode("utf-8")).hexdigest()
