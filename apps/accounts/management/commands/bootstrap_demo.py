
"""
python manage.py bootstrap_demo
Creates demo departments, sites, and all user types for both
ProcureDesk and OSH modules.
All passwords: password123
"""
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Bootstrap integrated system demo data."

    def handle(self, *args, **options):
        from apps.accounts.models import User, Site

        from apps.departments.models import Department

        self.stdout.write(self.style.MIGRATE_HEADING("\n── Site ──"))
        site, _ = Site.objects.get_or_create(code="HQ",
            defaults={"name":"Head Office","address":"Main Building"})
        self.stdout.write(f"  ✓ {site}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n── Departments ──"))
        depts = {}
        for name, code in [("Finance","FIN"),("IT","IT"),("Operations","OPS"),
                            ("HR","HR"),("Maintenance","MAINT"),("Production","PROD")]:
            dept, cr = Department.objects.get_or_create(code=code,
                defaults={"name":name,"site":site})
            depts[code] = dept
            self.stdout.write(f"  {"✓" if cr else " "} {dept}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n── Users ──"))
        def make(username, defaults):
            u, cr = User.objects.get_or_create(username=username, defaults=defaults)
            if cr: u.set_password("password123"); u.save(); self.stdout.write(f"  ✓ {username}")
            else: self.stdout.write(f"    {username} (exists)")
            return u

        # ProcureDesk users
        make("head_approver", {"first_name":"Head","last_name":"Approver","email":"head@example.com",
            "is_head_approver":True,"can_access_tickets":True,"is_asset_manager":True,"site":site})
        make("procurement",   {"first_name":"Jane","last_name":"Proc","email":"proc@example.com",
            "is_procurement_officer":True,"site":site})
        make("storekeeper",   {"first_name":"Store","last_name":"Keeper","email":"stores@example.com",
            "is_storekeeper":True,"site":site})
        make("stock_manager", {"first_name":"Stock","last_name":"Mgr","email":"stock@example.com",
            "is_stock_manager":True,"site":site})
        make("asset_manager", {"first_name":"Asset","last_name":"Mgr","email":"assets@example.com",
            "is_asset_manager":True,"site":site})
        make("gatekeeper",    {"first_name":"Gate","last_name":"Keeper","email":"gate@example.com",
            "is_gatekeeper":True,"site":site})
        make("ticket_viewer", {"first_name":"Ticket","last_name":"Viewer","email":"tv@example.com",
            "is_ticket_viewer":True,"can_access_tickets":True,"site":site})

        # OSH users
        make("hse_manager",  {"first_name":"HSE","last_name":"Manager","email":"hse.mgr@example.com",
            "osh_role":"manager","site":site,"department":depts["OPS"]})
        make("hse_officer",  {"first_name":"HSE","last_name":"Officer","email":"hse.off@example.com",
            "osh_role":"officer","site":site,"department":depts["OPS"]})
        make("auditor",      {"first_name":"Internal","last_name":"Auditor","email":"auditor@example.com",
            "osh_role":"auditor","site":site})

        # HODs (both systems)
        for code, dept in depts.items():
            make(f"hod_{code.lower()}", {
                "first_name":"HOD","last_name":dept.name,"email":f"hod.{code.lower()}@example.com",
                "department":dept,"is_hod":True,"can_access_tickets":True,"site":site,
                "osh_role":"employee"})
            make(f"staff_{code.lower()}", {
                "first_name":"Staff","last_name":dept.name,"email":f"staff.{code.lower()}@example.com",
                "department":dept,"can_access_tickets":True,"site":site,"osh_role":"employee"})

        self.stdout.write(self.style.MIGRATE_HEADING("\n── OSH Sample Data ──"))
        try:
            from apps.equipment.models import EquipmentCategory
            for name, days in [("Fire Extinguisher",90),("Machinery",365),("Electrical",180),("Emergency Equipment",90)]:
                EquipmentCategory.objects.get_or_create(name=name, defaults={"inspection_interval_days":days})
            self.stdout.write("  ✓ Equipment categories")
        except Exception as e:
            self.stdout.write(f"  ! Equipment categories: {e}")

        try:
            from apps.ppe.models import PPEType
            for name, months in [("Safety Helmet",24),("Safety Boots",18),("High-Vis Vest",12),
                                  ("Safety Gloves",6),("Safety Goggles",12),("Ear Protection",6)]:
                PPEType.objects.get_or_create(name=name, defaults={"lifespan_months":months})
            self.stdout.write("  ✓ PPE types")
        except Exception as e:
            self.stdout.write(f"  ! PPE types: {e}")

        self.stdout.write(self.style.SUCCESS("""
✓ Done. All passwords: password123

  ProcureDesk accounts:
    head_approver  procurement    storekeeper    stock_manager
    asset_manager  gatekeeper     ticket_viewer
    hod_fin/it/ops/hr/maint/prod
    staff_fin/it/ops/hr/maint/prod

  OSH accounts:
    hse_manager    hse_officer    auditor
"""))
