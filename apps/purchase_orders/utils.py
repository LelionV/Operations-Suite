from django.utils import timezone
from django.db import transaction
from .models import PurchaseOrder, POLineItem, ApprovalLog


class WorkflowError(Exception):
    pass


class POWorkflow:

    @staticmethod
    @transaction.atomic
    def submit(po, actor):
        if po.status != PurchaseOrder.Status.DRAFT:
            raise WorkflowError('Only draft POs can be submitted.')
        if po.requester != actor:
            raise WorkflowError('Only the requester can submit this PO.')
        if not po.line_items.filter(is_rejected=False).exists():
            raise WorkflowError('Add at least one active line item before submitting.')

        prev = po.status
        if actor.is_hod and actor.department == po.department:
            # HOD submitting own dept PO → auto-approve HOD stage, go straight to PENDING_HEAD
            po.status = PurchaseOrder.Status.PENDING_HEAD
            po.hod_approver = actor
            po.hod_approved_at = timezone.now()
            po.hod_auto = True
            po.save()
            ApprovalLog.objects.create(
                purchase_order=po, actor=actor,
                from_status=prev, to_status=po.status,
                comment='HOD auto-approval: requester is HOD of this department.',
            )
            from apps.notifications.utils import notify_on_hod_approval
            notify_on_hod_approval(po)
        else:
            po.status = PurchaseOrder.Status.PENDING_HOD
            po.save()
            ApprovalLog.objects.create(
                purchase_order=po, actor=actor,
                from_status=prev, to_status=po.status,
                comment='Submitted for HOD approval.',
            )
            from apps.notifications.utils import notify_on_submit
            notify_on_submit(po)

    @staticmethod
    @transaction.atomic
    def hod_approve(po, actor, comment=''):
        """
        HOD approves. Only valid when status is PENDING_HOD.
        Rejection at this stage keeps PO at PENDING_HOD (status → REJECTED,
        requester notified, PO does NOT move forward).
        """
        if not po.can_be_hod_approved_by(actor):
            raise WorkflowError('You do not have permission to perform HOD approval on this PO.')
        if po.status != PurchaseOrder.Status.PENDING_HOD:
            raise WorkflowError('This PO is not awaiting HOD approval.')

        prev = po.status
        po.status = PurchaseOrder.Status.PENDING_HEAD
        po.hod_approver = actor
        po.hod_approved_at = timezone.now()
        po.save()

        ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=prev, to_status=po.status,
            comment=comment or 'Approved by HOD.',
        )
        from apps.notifications.utils import notify_on_hod_approval
        notify_on_hod_approval(po)

    @staticmethod
    @transaction.atomic
    def head_approve(po, actor, comment=''):
        """
        Head approver gives final sign-off. Only valid when status is PENDING_HEAD
        AND hod_approver is already set (HOD has approved or auto-approved).
        Immediately moves to SENT_PROC for procurement.
        """
        if not po.can_be_head_approved_by(actor):
            raise WorkflowError('You do not have permission to give final approval on this PO.')
        if po.status != PurchaseOrder.Status.PENDING_HEAD:
            raise WorkflowError('This PO is not awaiting head approval.')
        if not po.hod_approver:
            raise WorkflowError('HOD must approve before head approval can be given.')

        prev = po.status
        po.status = PurchaseOrder.Status.APPROVED
        po.head_approver = actor
        po.head_approved_at = timezone.now()
        po.save()

        ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=prev, to_status=po.status,
            comment=comment or 'Final approval granted.',
        )
        from apps.notifications.utils import notify_on_head_approval
        notify_on_head_approval(po)

        # Auto-send to procurement
        POWorkflow._send_to_procurement(po, actor)

    @staticmethod
    @transaction.atomic
    def _send_to_procurement(po, actor):
        from apps.accounts.models import User
        proc = User.objects.filter(is_procurement_officer=True, is_active=True).first()
        prev = po.status
        po.status = PurchaseOrder.Status.SENT_PROC
        po.procurement_officer = proc
        po.sent_to_procurement_at = timezone.now()
        po.save()
        ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=prev, to_status=po.status,
            comment=f'Sent to procurement: {proc or "unassigned"}.',
        )
        from apps.notifications.utils import notify_procurement
        notify_procurement(po, proc)

    @staticmethod
    @transaction.atomic
    def reject(po, actor, reason):
        """
        Reject the whole PO. Status stays at the current review level as REJECTED.
        HOD can only reject at PENDING_HOD; Head can reject at PENDING_HEAD.
        Rejection is final — PO does not advance.
        """
        if not reason.strip():
            raise WorkflowError('A rejection reason is required.')
        if not po.can_be_rejected_by(actor):
            raise WorkflowError('You do not have permission to reject this PO at its current stage.')

        prev = po.status
        po.status = PurchaseOrder.Status.REJECTED
        po.rejection_reason = reason
        po.save()

        ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=prev, to_status=po.status,
            comment=reason,
        )
        from apps.notifications.utils import notify_on_rejection
        notify_on_rejection(po)

    @staticmethod
    @transaction.atomic
    def reject_items(po, actor, item_ids, reason):
        """
        Reject specific line items without rejecting the whole PO.
        If ALL items are rejected, the whole PO is then rejected.
        """
        if not po.can_reject_items_as(actor):
            raise WorkflowError('You do not have permission to reject items on this PO.')
        if not reason.strip():
            raise WorkflowError('A rejection reason is required.')
        if not item_ids:
            raise WorkflowError('Select at least one item to reject.')

        items = list(POLineItem.objects.filter(
            pk__in=item_ids, purchase_order=po, is_rejected=False))
        if not items:
            raise WorkflowError('No valid active items selected.')

        now = timezone.now()
        for item in items:
            item.is_rejected = True
            item.rejection_reason = reason
            item.rejected_by = actor
            item.rejected_at = now
            item.save()

        po.recalculate_total()

        log = ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=po.status, to_status=po.status,
            comment=f'Item(s) rejected: {reason}',
        )
        log.affected_items.set(items)

        from apps.notifications.utils import notify_items_rejected
        notify_items_rejected(po, items, reason)

        # If no active items remain → reject whole PO
        if not po.line_items.filter(is_rejected=False).exists():
            POWorkflow.reject(po, actor, reason=f'All items rejected. {reason}')

    @staticmethod
    @transaction.atomic
    def cancel(po, actor):
        if not po.can_be_cancelled_by(actor):
            raise WorkflowError('You cannot cancel this PO at its current stage.')
        prev = po.status
        po.status = PurchaseOrder.Status.CANCELLED
        po.save()
        ApprovalLog.objects.create(
            purchase_order=po, actor=actor,
            from_status=prev, to_status=po.status,
            comment='Cancelled.',
        )
