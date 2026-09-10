
from django.core.mail import get_connection, EmailMessage

def _cfg():
    try:
        from apps.settings_manager.models import SystemSetting
        return SystemSetting.get_email_config()
    except Exception:
        return {"EMAIL_ENABLED": False}

def _email(subject, body, recipients):
    if not recipients: return
    cfg=_cfg()
    if not cfg.get("EMAIL_ENABLED"): return
    try:
        conn=get_connection(backend="django.core.mail.backends.smtp.EmailBackend",
            host=cfg.get("EMAIL_HOST",""),port=int(cfg.get("EMAIL_PORT") or 587),
            username=cfg.get("EMAIL_HOST_USER",""),password=cfg.get("EMAIL_HOST_PASSWORD",""),
            use_tls=cfg.get("EMAIL_USE_TLS",True),use_ssl=cfg.get("EMAIL_USE_SSL",False),fail_silently=True)
        msg=EmailMessage(subject=subject,body=body,
            from_email=cfg.get("DEFAULT_FROM_EMAIL","noreply@po-system.com"),
            to=[r for r in recipients if r],connection=conn)
        msg.content_subtype="html"; msg.send(fail_silently=True)
    except Exception: pass

def _notify(recipient, kind, title, body="", link=""):
    try:
        from apps.notify.models import Notification
        Notification.send(recipient,kind=kind,title=title,body=body,link=link)
    except Exception: pass

def notify_on_submit(po):
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    if po.hod_auto: notify_on_hod_approval(po); return
    hod=po.department.get_hod()
    if hod:
        _notify(hod,"po_submitted",f"PO Approval Needed: {po.po_number}",
            f"{po.requester.get_full_name()} submitted {po.po_number}",link)
        if hod.email:
            _email(f"[ProcureDesk] PO Approval Needed: {po.po_number}",
                f"<p>Dear {hod.get_full_name()},</p><p>{po.requester.get_full_name()} submitted <b>{po.po_number}</b> ({po.title}) for your approval.</p>",[hod.email])

def notify_on_hod_approval(po):
    from apps.accounts.models import User
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    head=User.objects.filter(is_head_approver=True,is_active=True).first()
    if head:
        _notify(head,"po_submitted",f"Final Approval Needed: {po.po_number}",
            f"{po.po_number} passed HOD — needs your sign-off.",link)
        if head.email:
            _email(f"[ProcureDesk] Final Approval Needed: {po.po_number}",
                f"<p>Dear {head.get_full_name()},</p><p><b>{po.po_number}</b> ({po.title}) needs your final approval.</p>",[head.email])

def notify_on_head_approval(po):
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    _notify(po.requester,"po_approved",f"PO Approved: {po.po_number}",
        f"Your PO {po.po_number} has been approved.",link)
    if po.requester.email:
        _email(f"[ProcureDesk] PO Approved: {po.po_number}",
            f"<p>Dear {po.requester.get_full_name()},</p><p>Your PO <b>{po.po_number}</b> ({po.title}) has been approved.</p>",[po.requester.email])

def notify_on_rejection(po):
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    _notify(po.requester,"po_rejected",f"PO Rejected: {po.po_number}",po.rejection_reason,link)
    if po.requester.email:
        _email(f"[ProcureDesk] PO Rejected: {po.po_number}",
            f"<p>Dear {po.requester.get_full_name()},</p><p><b>{po.po_number}</b> was rejected.</p><p><b>Reason:</b> {po.rejection_reason}</p>",[po.requester.email])

def notify_items_rejected(po, items, reason):
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    names=", ".join(f"{i.code} ({i.description})" for i in items)
    _notify(po.requester,"po_rejected",f"Items Rejected on {po.po_number}",f"{names} — {reason}",link)
    if po.requester.email:
        _email(f"[ProcureDesk] Items Rejected on {po.po_number}",
            f"<p>{names} were rejected on <b>{po.po_number}</b>. Reason: {reason}</p>",[po.requester.email])

def notify_procurement(po, proc_officer):
    if not proc_officer: return
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    items="".join(f"<li>{i.code} | {i.description} | Qty: {i.quantity}</li>" for i in po.active_line_items)
    _notify(proc_officer,"po_sent_proc",f"New PO for Procurement: {po.po_number}",
        f"{po.po_number} is approved and ready.",link)
    if proc_officer.email:
        _email(f"[ProcureDesk] New PO for Procurement: {po.po_number}",
            f"<p>PO <b>{po.po_number}</b> ({po.title}) is ready for procurement.</p><ul>{items}</ul>",[proc_officer.email])

def notify_order_placed(po, proc_order):
    from apps.accounts.models import User
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    dept_users=list(User.objects.filter(department=po.department,is_active=True))
    all_users=list({u.pk:u for u in [po.requester]+dept_users}.values())
    for u in all_users:
        _notify(u,"po_ordered",f"Order Placed: {po.po_number}",
            f"Supplier: {proc_order.supplier_name or 'TBD'}",link)
    emails=[u.email for u in all_users if u.email]
    if emails:
        _email(f"[ProcureDesk] Order Placed: {po.po_number}",
            f"<p>Order placed for <b>{po.po_number}</b> ({po.title}).<br>Supplier: {proc_order.supplier_name or 'TBD'}</p>",emails)

def notify_stores_on_order(po):
    from apps.accounts.models import User
    from django.urls import reverse
    link=reverse("stores:dashboard")
    storekeepers=list(User.objects.filter(is_storekeeper=True,is_active=True))
    for u in storekeepers: _notify(u,"po_ordered",f"Items Ordered: {po.po_number}","Ready to receive.",link)
    emails=[u.email for u in storekeepers if u.email]
    if emails:
        _email(f"[ProcureDesk] Items Ordered: {po.po_number}",
            f"<p>PO <b>{po.po_number}</b> has been ordered and goods will arrive soon.</p>",emails)

def notify_grn_created(po, grn):
    from apps.accounts.models import User
    from django.urls import reverse
    link=reverse("stores:grn_detail",kwargs={"pk":grn.pk})
    dept_users=list(User.objects.filter(department=po.department,is_active=True))
    all_users=list({u.pk:u for u in [po.requester]+dept_users}.values())
    for u in all_users:
        _notify(u,"grn_created",f"Goods Received: {po.po_number}",f"GRN {grn.grn_number}",link)
    emails=[u.email for u in all_users if u.email]
    items="".join(f"<li>{g.code}: {g.qty_received}/{g.qty_ordered} {g.uom}</li>" for g in grn.grn_items.all())
    if emails:
        _email(f"[ProcureDesk] Goods Received: {po.po_number}",
            f"<p>GRN <b>{grn.grn_number}</b> created.<br>Status: {grn.get_status_display()}</p><ul>{items}</ul>",emails)

def notify_po_deadline(po):
    from django.urls import reverse
    link=reverse("purchase_orders:detail",kwargs={"pk":po.pk})
    _notify(po.requester,"po_deadline",f"PO Submission Deadline: {po.po_number}",
        f"Your PO {po.po_number} has not been submitted and the deadline is approaching.",link)
    if po.requester.email:
        _email(f"[ProcureDesk] Action Required — PO Deadline: {po.po_number}",
            f"<p>Dear {po.requester.get_full_name()},</p>"
            f"<p>Your PO <b>{po.po_number}</b> ({po.title}) has not been submitted. "
            f"The submission deadline is <b>{po.submission_deadline.strftime('%d %b %Y %H:%M')}</b>.</p>"
            f"<p>Please log in and submit your PO.</p>",[po.requester.email])
    po.deadline_notification_sent=True
    po.save(update_fields=["deadline_notification_sent"])
