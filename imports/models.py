from django.db import models


class ImportBatch(models.Model):
    class SourceMode(models.TextChoices):
        LOCAL = "local", "Local"
        SFTP = "sftp", "SFTP"

    class Status(models.TextChoices):
        PROCESSING = "processing", "Processando"
        SUCCESS = "success", "Sucesso"
        ERROR = "error", "Erro"
        DUPLICATED = "duplicated", "Duplicado"
        FILE_NOT_FOUND = "file_not_found", "Arquivo não encontrado"
        VALIDATION_ERROR = "validation_error", "Erro de validação"

    source_mode = models.CharField(max_length=20, choices=SourceMode.choices)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    file_hash = models.CharField(max_length=64, db_index=True)
    sheet_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROCESSING,
        db_index=True,
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)
    invalid_rows = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    technical_details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at", "-id"]
        indexes = [
            models.Index(fields=["source_mode"], name="imports_batch_source_idx"),
            models.Index(fields=["started_at"], name="imports_batch_started_idx"),
            models.Index(fields=["file_hash", "status"], name="imports_batch_hash_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["file_hash"],
                condition=models.Q(status="success"),
                name="unique_successful_import_batch_hash",
            )
        ]

    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()}"


class LeadTimeRecord(models.Model):
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE,
        related_name="lead_time_records",
    )
    row_number = models.PositiveIntegerField()
    row_hash = models.CharField(max_length=64, db_index=True)
    business_unit = models.CharField(max_length=80, db_index=True)

    map_date = models.DateField()
    map_number = models.CharField(max_length=30)
    owner = models.CharField(max_length=150)
    route = models.CharField(max_length=30, db_index=True)
    delivery_points = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=14, decimal_places=3)
    volume = models.DecimalField(max_digits=14, decimal_places=3)
    map_value = models.DecimalField(max_digits=14, decimal_places=2)
    vehicle_plate = models.CharField(max_length=20)
    driver_code = models.CharField(max_length=30, blank=True)
    driver_name = models.CharField(max_length=150, blank=True, db_index=True)
    checker_code = models.CharField(max_length=30, blank=True)
    checker_name = models.CharField(max_length=150, blank=True)
    load_status_description = models.CharField(max_length=80)
    load_date = models.DateField(db_index=True)

    invoice_number = models.CharField(max_length=30)
    invoice_series = models.CharField(max_length=20)
    invoice_issue_date = models.DateField(db_index=True)
    bordero_number = models.CharField(max_length=30)
    customer_code = models.CharField(max_length=30)
    customer_name = models.CharField(max_length=255)
    city = models.CharField(max_length=120, db_index=True)
    region = models.CharField(max_length=80, blank=True, db_index=True)
    frequency = models.CharField(max_length=80, blank=True, db_index=True)
    invoice_value = models.DecimalField(max_digits=14, decimal_places=2)
    invoice_status = models.CharField(max_length=50)
    cargo_status = models.CharField(max_length=50, db_index=True)
    auxiliary_date = models.DateField(null=True, blank=True)
    delivery_status = models.CharField(max_length=50, db_index=True)
    customer_delivery_date = models.DateField(null=True, blank=True, db_index=True)
    customer_delivery_time = models.TimeField(null=True, blank=True)
    customer_delivery_datetime = models.DateTimeField(null=True, blank=True)

    exported_to = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    seller_code = models.CharField(max_length=30)
    team_code = models.CharField(max_length=30)

    operational_lead_time_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    carrier_lead_time_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_operational_late = models.BooleanField(default=False)
    is_carrier_late = models.BooleanField(default=False)
    business_days_count = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["invoice_issue_date", "invoice_number", "id"]
        indexes = [
            models.Index(fields=["import_batch"], name="imports_record_batch_idx"),
            models.Index(fields=["invoice_issue_date", "driver_name"], name="imp_rec_issue_driver_idx"),
            models.Index(fields=["customer_delivery_date", "driver_name"], name="imp_rec_delivery_driver_idx"),
            models.Index(fields=["invoice_number", "invoice_series"], name="imports_record_invoice_idx"),
            models.Index(fields=["business_unit", "invoice_issue_date"], name="imports_record_unit_issue_idx"),
            models.Index(fields=["region"], name="imports_record_region_idx"),
            models.Index(fields=["frequency"], name="imports_record_freq_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["import_batch", "row_number"],
                name="unique_lead_time_record_batch_row",
            )
        ]

    def __str__(self):
        return f"NF {self.invoice_number} - {self.customer_name}"
