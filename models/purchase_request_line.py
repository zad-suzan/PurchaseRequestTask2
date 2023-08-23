# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = []

    product_id = fields.Many2one("product.product", string="Product", required=True)
    Description = fields.Char(string='Description', related="product_id.name")
    Quantity = fields.Float(string="Quantity", default=1)
    Cost = fields.Float(string="Cost Price", related = 'product_id.standard_price', readonly=True)
    Total = fields.Float(string='Total', compute='_compute_total', readonly=True)
    Ordered_Quantity = fields.Float(string='Ordered Quantity',compute= '_onchange_ordered_quantity' )
    Quantity_To_order = fields.Float(string='Quantity_To_order', default=1)
    pur_req_id = fields.Many2one('purchase.request', string='Purchase Request')
    # pur_req = fields.Many2one('purchase.request')
    po_id = fields.Many2one('purchase.order')
    po_lines = fields.One2many('purchase.order.line','pur_req_line')

    @api.depends('Quantity','Cost')
    def _compute_total(self):
        for rec in self:
            rec.Total = rec.Quantity * rec.Cost

    # @api.depends('Quantity')
    # def _compute_ordered_quantity(self):
    #     for rec in self:
    #         rec.Ordered_Quantity = 0

    @api.depends()
    def _onchange_ordered_quantity(self):
        for rec in self:
            pr = self.env['purchase.request'].search([])

            print('_onchange_ordered_quantity',pr)
            print(rec.po_lines)
            rec.Ordered_Quantity = sum(line.product_qty for line in rec.po_lines)



