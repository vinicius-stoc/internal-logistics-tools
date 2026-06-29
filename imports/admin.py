from django.contrib import admin

from .models import ImportBatch, LeadTimeRecord


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "source_mode",
        "sheet_name",
        "status",
        "total_rows",
        "valid_rows",
        "invalid_rows",
        "started_at",
        "finished_at",
    )
    list_filter = ("source_mode", "status", "sheet_name", "started_at")
    search_fields = ("file_name", "file_hash")
    readonly_fields = ("created_at", "updated_at")


@admin.register(LeadTimeRecord)
class LeadTimeRecordAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "business_unit",
        "driver_name",
        "city",
        "region",
        "frequency",
        "invoice_issue_date",
        "customer_delivery_date",
        "delivery_status",
        "is_operational_late",
        "is_carrier_late",
    )
    list_filter = (
        "business_unit",
        "region",
        "frequency",
        "delivery_status",
        "cargo_status",
        "is_operational_late",
        "is_carrier_late",
        "invoice_issue_date",
    )
    search_fields = (
        "invoice_number",
        "map_number",
        "driver_name",
        "customer_name",
        "city",
        "region",
        "frequency",
        "vehicle_plate",
    )
    readonly_fields = ("created_at", "updated_at")
