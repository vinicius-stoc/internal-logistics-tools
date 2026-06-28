import json
from datetime import date, time
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from dashboard.services.dashboard_filters import DashboardFilters
from dashboard.services.dashboard_queries import get_dashboard_context
from imports.models import ImportBatch, LeadTimeRecord


class DashboardAnalyticsTests(TestCase):
    def test_empty_dashboard_context_is_serializable(self):
        context = get_dashboard_context(DashboardFilters())

        self.assertEqual(context["cards"]["total_records"], 0)
        self.assertEqual(context["cards"]["total_invoice_value"], "0.00")
        self.assertFalse(context["metadata"]["has_data"])
        self.assertIsNone(context["metadata"]["last_successful_import"])
        self.assertIn("records_by_day", context["charts"])

        json.dumps(context)

    def test_cards_are_calculated_from_filtered_records(self):
        batch = self._create_batch()
        self._create_record(
            batch=batch,
            row_number=1,
            invoice_number="1001",
            invoice_issue_date=date(2026, 5, 1),
            invoice_value=Decimal("100.00"),
            delivery_status="ENTREGUE",
            operational_lead_time_hours=Decimal("10.00"),
            carrier_lead_time_hours=Decimal("5.00"),
            is_operational_late=True,
            is_carrier_late=False,
        )
        self._create_record(
            batch=batch,
            row_number=2,
            invoice_number="1002",
            invoice_issue_date=date(2026, 5, 2),
            invoice_value=Decimal("50.50"),
            delivery_status="PENDENTE",
            operational_lead_time_hours=Decimal("20.00"),
            carrier_lead_time_hours=Decimal("7.00"),
            is_operational_late=False,
            is_carrier_late=True,
        )

        context = get_dashboard_context(DashboardFilters())
        cards = context["cards"]

        self.assertEqual(cards["total_records"], 2)
        self.assertEqual(cards["delivered_records"], 1)
        self.assertEqual(cards["pending_records"], 1)
        self.assertEqual(cards["total_invoice_value"], "150.50")
        self.assertEqual(cards["average_operational_lead_time_hours"], "15.00")
        self.assertEqual(cards["average_carrier_lead_time_hours"], "6.00")
        self.assertEqual(cards["operational_late_records"], 1)
        self.assertEqual(cards["carrier_late_records"], 1)
        self.assertEqual(cards["operational_late_percentage"], "50.00")
        self.assertEqual(cards["carrier_late_percentage"], "50.00")

    def test_filters_are_applied_to_queryset(self):
        batch = self._create_batch()
        self._create_record(
            batch=batch,
            row_number=1,
            invoice_number="1001",
            driver_name="BEATRIZ GOMES",
            route="RT030",
            business_unit="TABACO",
            delivery_status="ENTREGUE",
            cargo_status="Ativa",
            invoice_issue_date=date(2026, 5, 1),
        )
        self._create_record(
            batch=batch,
            row_number=2,
            invoice_number="1002",
            driver_name="ANA SILVA",
            route="RT010",
            business_unit="ALIMENTOS",
            delivery_status="PENDENTE",
            cargo_status="Cancelada",
            invoice_issue_date=date(2026, 6, 1),
        )

        filters = DashboardFilters(
            date_start=date(2026, 5, 1),
            date_end=date(2026, 5, 31),
            driver_name="BEATRIZ GOMES",
            route="RT030",
            business_unit="TABACO",
            delivery_status="ENTREGUE",
            cargo_status="Ativa",
        )
        context = get_dashboard_context(filters)

        self.assertEqual(context["cards"]["total_records"], 1)
        self.assertEqual(context["tables"]["driver_summary"][0]["driver_name"], "BEATRIZ GOMES")
        self.assertEqual(context["tables"]["route_summary"][0]["route"], "RT030")

    def test_chart_contracts_have_stable_json_shape(self):
        batch = self._create_batch()
        self._create_record(
            batch=batch,
            row_number=1,
            invoice_number="1001",
            driver_name="BEATRIZ GOMES",
            route="RT030",
            invoice_issue_date=date(2026, 5, 1),
            delivery_status="ENTREGUE",
        )
        self._create_record(
            batch=batch,
            row_number=2,
            invoice_number="1002",
            driver_name="BEATRIZ GOMES",
            route="RT030",
            invoice_issue_date=date(2026, 5, 2),
            delivery_status="PENDENTE",
        )

        charts = get_dashboard_context(DashboardFilters())["charts"]

        self.assertEqual(charts["records_by_day"]["id"], "records_by_day")
        self.assertEqual(charts["records_by_day"]["type"], "bar")
        self.assertEqual(charts["records_by_day"]["data"]["labels"], ["2026-05-01", "2026-05-02"])
        self.assertEqual(charts["records_by_driver"]["data"]["labels"], ["BEATRIZ GOMES"])
        self.assertEqual(charts["records_by_route"]["data"]["labels"], ["RT030"])
        self.assertEqual(charts["delivery_status_distribution"]["type"], "doughnut")
        self.assertEqual(len(charts["lead_time_by_driver"]["data"]["datasets"]), 2)

        json.dumps(charts)

    def test_last_successful_import_ignores_failed_batches(self):
        self._create_batch(status=ImportBatch.Status.ERROR, file_hash="error-hash")
        success_batch = self._create_batch(status=ImportBatch.Status.SUCCESS, file_hash="success-hash")

        metadata = get_dashboard_context(DashboardFilters())["metadata"]

        self.assertEqual(metadata["last_successful_import"]["id"], success_batch.id)
        self.assertEqual(metadata["last_successful_import"]["status"], ImportBatch.Status.SUCCESS)

    def test_invalid_date_filter_is_ignored_safely(self):
        filters = DashboardFilters.from_querydict({"date_start": "invalid-date"})

        self.assertIsNone(filters.date_start)
        self.assertEqual(filters.errors, ["date_start must use YYYY-MM-DD."])
        self.assertEqual(get_dashboard_context(filters)["cards"]["total_records"], 0)

    def _create_batch(self, status=ImportBatch.Status.SUCCESS, file_hash="file-hash"):
        now = timezone.now()
        return ImportBatch.objects.create(
            source_mode=ImportBatch.SourceMode.LOCAL,
            file_name=f"{file_hash}.xlsx",
            file_path="data/test.xlsx",
            file_hash=file_hash,
            sheet_name="COM 001",
            status=status,
            started_at=now,
            finished_at=now if status == ImportBatch.Status.SUCCESS else None,
            total_rows=1,
            valid_rows=1 if status == ImportBatch.Status.SUCCESS else 0,
            invalid_rows=0,
        )

    def _create_record(self, batch, row_number, invoice_number, **overrides):
        defaults = {
            "row_hash": f"row-hash-{row_number}",
            "business_unit": "TABACO",
            "map_date": date(2026, 5, 1),
            "map_number": "470939",
            "owner": "948 TAINARA CAMARGO MONTE",
            "route": "RT030",
            "delivery_points": 18,
            "weight": Decimal("151.670"),
            "volume": Decimal("0.640"),
            "map_value": Decimal("375.10"),
            "vehicle_plate": "AZP8G94",
            "driver_code": "395",
            "driver_name": "BEATRIZ GOMES",
            "checker_code": "",
            "checker_name": "",
            "load_status_description": "CARREGADO EM",
            "load_date": date(2026, 5, 5),
            "invoice_series": "11",
            "invoice_issue_date": date(2026, 5, 4),
            "bordero_number": "807679",
            "customer_code": "6248888",
            "customer_name": "CLIENTE TESTE LTDA",
            "city": "PONTA GROSSA",
            "invoice_value": Decimal("1674.40"),
            "invoice_status": "AZP8G94",
            "cargo_status": "Ativa",
            "auxiliary_date": None,
            "delivery_status": "ENTREGUE",
            "customer_delivery_date": date(2026, 5, 5),
            "customer_delivery_time": time(16, 12),
            "customer_delivery_datetime": timezone.now(),
            "exported_to": "UMOV",
            "notes": "",
            "seller_code": "681",
            "team_code": "1",
            "operational_lead_time_hours": Decimal("10.00"),
            "carrier_lead_time_hours": Decimal("5.00"),
            "is_operational_late": False,
            "is_carrier_late": False,
            "business_days_count": 1,
        }
        defaults.update(overrides)

        return LeadTimeRecord.objects.create(
            import_batch=batch,
            row_number=row_number,
            invoice_number=invoice_number,
            **defaults,
        )
