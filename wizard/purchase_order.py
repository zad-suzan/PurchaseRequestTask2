from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderWizard(models.TransientModel):
    _name = "purchase.order.wizard"
    _description = "Purchase Order"

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
    pr_sdate = fields.Date(related="purchase_request_id.StartDate")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    order_line_ids = fields.One2many("purchase.order.wizard.line", "order_wizard")
    pr_lines = fields.Many2one('purchase.request.line')
    po_lines = fields.Many2one('purchase.order.line')

    def default_get(self, fields):
        result = super(PurchaseOrderWizard, self).default_get(fields)
        result['purchase_request_id'] = self.env.context.get('active_id')
        return result

    def create_purchase_order(self):
        self.compute_ordered_quantity()
        order_lines = []
        for line in self.order_line_ids:
            line.pur_req_line.Ordered_Quantity += line.prod_Quant_to_order
            order_lines.append((0, 0, {
                'name': line.prod_name,
                'product_id': line.product_id.id,
                'product_qty': line.prod_Quant_to_order,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
                'price_unit': line.product_id.standard_price,
                'pur_req_line':line.pur_req_line.id,
            }))

        po = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': order_lines,
            'date_order': fields.Date.today(),
            'pur_req': self.purchase_request_id.id,
        })

    def compute_ordered_quantity(self):
        for rec in self:
            for product in rec.order_line_ids:
                if product.prod_Quant_to_order <= product.prod_Remaining_Quantity:
                    product.prod_Ordered_Quantity += product.prod_Quant_to_order
                    product.prod_Remaining_Quantity -= product.prod_Quant_to_order
                else:
                    raise ValidationError("Quantity to Order can't exceed Needed Quantity")

class PurchaseOrderWizardLine(models.TransientModel):
    _name = "purchase.order.wizard.line"
    _description = "Purchase Order Line"

    order_wizard = fields.Many2one("purchase.order.wizard")
    pur_req_line = fields.Many2one('purchase.request.line',store=True)
    product_id = fields.Many2one("product.product", readonly=True)
    prod_name = fields.Char(string="Product", readonly=True)
    prod_Quantity = fields.Float(readonly=True)
    prod_Ordered_Quantity = fields.Float(string="Ordered Quantity", readonly=True)
    prod_Remaining_Quantity = fields.Float(string="Remaining Quantity")
    prod_Quant_to_order = fields.Float(string="Quantity To Order")
