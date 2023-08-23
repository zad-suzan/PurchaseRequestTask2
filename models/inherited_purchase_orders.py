# -*- coding: utf-8 -*-
from odoo import api, fields, models


class InheritedPurchaseOrderLines(models.Model):
    _inherit = 'purchase.order.line'

    pur_req_line = fields.Many2one('purchase.request.line')


class InheritedPurchaseOrders(models.Model):
    _inherit = 'purchase.order'

    pur_req = fields.Many2one('purchase.request')

