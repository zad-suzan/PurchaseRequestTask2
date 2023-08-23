from odoo import api, fields, models
from odoo.exceptions import ValidationError

class RejectPurchaseRequestWizard(models.TransientModel):
    _name = "reject.purchase.request.wizard"
    _description = "Reject Purchase Request"

    rejection_reason = fields.Text(string="Rejection Reason")

    def confirm_rejection(self):
        # On click confirm button, Check the rejection_reason field to make sure it is filled
        if self.rejection_reason:
            purchase_request = self.env['purchase.request'].browse(self.env.context.get('active_id'))
            purchase_request.write({'RejectionReason': self.rejection_reason, 'state': 'reject'})
        else:
            raise ValidationError("Rejection Reason is mandatory!")

    def cancel(self):
        # On click cancel button, Just close the wizard
        pass
