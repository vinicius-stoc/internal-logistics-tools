from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from imports.models import ImportBatch
from imports.services.lead_time_import_service import LeadTimeImportService


class Command(BaseCommand):
    help = "Importa registros de lead time a partir da planilha local configurada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file-path",
            dest="file_path",
            help="Sobrescreve LOCAL_EXCEL_PATH para uma execução local específica.",
        )
        parser.add_argument(
            "--source-mode",
            dest="source_mode",
            choices=[ImportBatch.SourceMode.LOCAL],
            help="Origem da importação. Nesta etapa, apenas local é suportado.",
        )

    def handle(self, *args, **options):
        source_mode = options["source_mode"] or settings.EXCEL_SOURCE_MODE
        if source_mode != ImportBatch.SourceMode.LOCAL:
            raise CommandError(
                "EXCEL_SOURCE_MODE não suportado nesta etapa. Use apenas local."
            )

        file_path = options["file_path"] or settings.LOCAL_EXCEL_PATH
        resolved_path = self._resolve_path(file_path)

        batch = LeadTimeImportService().import_file(
            resolved_path,
            source_mode=source_mode,
        )

        self._write_batch_result(batch)
        if batch.status in {
            ImportBatch.Status.ERROR,
            ImportBatch.Status.FILE_NOT_FOUND,
            ImportBatch.Status.VALIDATION_ERROR,
        }:
            raise CommandError(batch.error_message or "Importação não concluída.")

    def _resolve_path(self, file_path):
        path = Path(file_path)
        if not path.is_absolute():
            path = settings.BASE_DIR / path
        return path

    def _write_batch_result(self, batch):
        if batch.status == ImportBatch.Status.SUCCESS:
            self.stdout.write(
                self.style.SUCCESS(
                    "Importação concluída. "
                    f"Batch #{batch.id} | válidas: {batch.valid_rows} | "
                    f"inválidas: {batch.invalid_rows}"
                )
            )
            return

        if batch.status == ImportBatch.Status.DUPLICATED:
            self.stdout.write(
                self.style.WARNING(
                    f"Arquivo já importado. Batch #{batch.id} marcado como duplicado."
                )
            )
            return

        if batch.status == ImportBatch.Status.FILE_NOT_FOUND:
            self.stdout.write(
                self.style.ERROR(
                    f"Importação não executada: arquivo não encontrado. Batch #{batch.id}"
                )
            )
            return

        if batch.status == ImportBatch.Status.VALIDATION_ERROR:
            self.stdout.write(
                self.style.ERROR(
                    f"Importação não executada: erro de validação. Batch #{batch.id}"
                )
            )
            return

        self.stdout.write(
            self.style.ERROR(
                f"Importação não concluída. Batch #{batch.id} | status: {batch.status}"
            )
        )
