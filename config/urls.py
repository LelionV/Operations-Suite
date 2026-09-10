
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/pos/", permanent=False)),
    path("admin/", admin.site.urls),

    # ── Auth ──────────────────────────────────────────────────────────────
    path("accounts/", include("apps.accounts.urls")),

    # ── Notifications ──────────────────────────────────────────────────────
    path("notify/", include("apps.notify.urls")),

    # ── ProcureDesk ──────────────────────────────────────────────────────
    path("departments/",  include("apps.departments.urls")),
    path("inventory/",    include("apps.inventory.urls")),
    path("pos/",          include("apps.purchase_orders.urls")),
    path("procurement/",  include("apps.procurement.urls")),
    path("stores/",       include("apps.stores.urls")),
    path("stock/",        include("apps.stock.urls")),
    path("assets/",       include("apps.assets.urls")),
    path("tickets/",      include("apps.tickets.urls")),
    path("visitors/",     include("apps.visitors.urls")),
    path("system/",       include("apps.settings_manager.urls")),

    # ── OSH / EHS ────────────────────────────────────────────────────────
    # path("osh/",              include("apps.dashboard.urls")),
    path("compliance/",       include("apps.compliance.urls")),
    path("policies/",         include("apps.policies.urls")),
    path("risks/",            include("apps.risks.urls")),
    path("hse-equipment/",    include("apps.equipment.urls")),
    path("inspections/",      include("apps.inspections.urls")),
    path("maintenance/",      include("apps.maintenance.urls")),
    path("ppe/",              include("apps.ppe.urls")),
    path("training/",         include("apps.training.urls")),
    path("audits/",           include("apps.audits.urls")),
    path("incidents/",        include("apps.incidents.urls")),
    path("nonconformities/",  include("apps.nonconformities.urls")),
    path("capa/",             include("apps.actions.urls")),
    path("licenses/",         include("apps.licenses.urls")),
    path("contractors/",      include("apps.contractors.urls")),
    path("environmental/",    include("apps.environmental.urls")),
    path("chemicals/",        include("apps.chemicals.urls")),
    path("emergency/",        include("apps.emergency.urls")),
    path("evidence/",         include("apps.evidence.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
