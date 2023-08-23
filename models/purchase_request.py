# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import date


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Purchase Request"

    @api.model_create_multi
    def create(self, vals):
        vals= merge_prod_qty(self,vals)
        return super(PurchaseRequest, self).create(vals)

    def write(self, vals):
        if 'orderlines' in vals:
            mine = [vals]
            vals = merge_prod_qty(self,mine)
            vals = vals[0]
            self.orderlines.unlink()
        res = super(PurchaseRequest, self).write(vals)
        return res

    name = fields.Char(string='Request Name', required=True,
                       states={'approved': [('readonly', True)],
                               'reject': [('readonly', True)], 'cancel': [('readonly', True)]})
    req_by = fields.Many2one("res.users", string="Requested by", required=True, default=lambda self: self.env.user.id,
                             states={'approved': [('readonly', True)],
                                     'reject': [('readonly', True)], 'cancel': [('readonly', True)]})
    StartDate = fields.Date(string="Start Date", default=date.today(),
                            states={'approved': [('readonly', True)],
                                    'reject': [('readonly', True)], 'cancel': [('readonly', True)]})
    EndDate = fields.Date(string="End Date",
                          states={'approved': [('readonly', True)],
                                  'reject': [('readonly', True)], 'cancel': [('readonly', True)]})
    RejectionReason = fields.Text(string="Rejection Reason", readonly=True)
    orderlines = fields.One2many('purchase.request.line', 'pur_req_id',string='Order Lines',
                                 states={'approved': [('readonly', True)],
                                         'reject': [('readonly', True)], 'cancel': [('readonly', True)]})
    # orderlines = fields.One2many('purchase.request.line', 'pur_req', default=_merge_product_qtys)
    TotalPrice = fields.Float(string="Total Price", compute='_compute_total_price', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('to_be_approved', 'To Be Approved'),
                              ('approved', 'Approved'),
                              ('reject', 'Rejected'),
                              ('cancel', 'Cancel')],
                             default="draft", string="Status")
    # po_ids = fields.One2many('purchase.order.wizard', 'purchase_request_id', string='Purchase Orders')
    partner_id= fields.Many2one('res.partner')
    remove_po = fields.Boolean(compute='_compute_remove_po')
    po_count = fields.Integer(compute="_compute_po_count")
    pur_orders = fields.One2many("purchase.order","pur_req")

    def _compute_po_count(self):
        for rec in self:
            rec.po_count = len(rec.pur_orders)
        #     count = 0
        #     for order in rec.pur_orders:
        #         count+=1
        # rec.po_count= count

    @api.depends('orderlines')
    def _compute_total_price(self):
        for rec in self:
            sum = 0
            for order in rec.orderlines:
                sum += order.Total
            rec.TotalPrice=sum

    def submit_for_approval(self):
        self.state= "to_be_approved"

    def action_to_cancel(self):
        self.state= "cancel"

    def approve(self):
        # On click approve button, change the state and send an email to purchase_manager group
        self.state= "approved"
        purchase_managers = self.env.ref('Purchase.group_purchase_manager').users
        recipients = purchase_managers.mapped('partner_id.email')
        subject = f"Purchase Request ({self.name}) has been approved"
        body = f"Dear Purchase Manager,\n\nThe purchase request ({self.name}) has been approved.\n\nBest regards and have a great day."
        self.env['mail.mail'].create({
            'subject': subject,
            'body_html': body,
            'email_to': ','.join(recipients)
        })

    def action_create_po(self):
        lines = []
        for line in self.orderlines:
            lines.append((0,0,{
                'pur_req_line': line.id,
                'product_id': line.product_id.id,
                'prod_name': line.product_id.name,  # order.Description
                'prod_Quantity': line.Quantity,
                'prod_Ordered_Quantity': line.Ordered_Quantity,
                'prod_Remaining_Quantity': line.Quantity - line.Ordered_Quantity
            }))
        print('lines 121: ',lines)
        ctx = dict(
            default_order_line_ids=lines,
        )
        return {
            'name': _('create po'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.wizard',
            'target': 'new',
            'context': ctx,
        }

    def reject(self):
        self.state= "reject"

    def reset_to_draft(self):
        self.state= "draft"

    def action_view_pos(self):
        return



    def create_po(self):
        pass
        # now = self.env.context.get('active_id')
        # po = self.env['purchase.order'].create({'partner_id': self.partner_a.id})
        #
        # my_products = []
        # for order in self.orderlines:
        #     my_products.append((0, 0, {
        #         'product_id': order.product_id.id,
        #         'name': order.Description,
        #         'price_unit': order.Cost,
        #         'product_qty': order.Quantity,
        #     }))
        #
        # po = self.env['purchase.order'].create({'partner_id': self.partner_a.id})
        # self.env['purchase.order.line'].create({
        #     'order_id': po.id,
        #     'name': 'test',
        #     'product_id': self.product_a.id
        # })


        #
        # po = self.env['purchase.order'].create({
        #     'partner_id': self.partner_id.id,
        #     'purchase_request_id': self.id,
        #     'order_line': my_products,
        # })



        # view_id = self.env.ref('Purchase.view_purchase_order_wizard_form').id
        # # view_id = self.env.ref('your_module_name.purchase_request_wizard_form_view').id
        # lines = []
        #
        # for line in self.orderlines:
        #     lines.append((0, 0, {
        #         'product_id': line.product_id.id,
        #         'description': line.description,
        #         'quantity': line.quantity,
        #         'cost': line.cost,
        #
        #     }))
        # wizard = self.env['purchase.request.wizard'].create({
        #     'partner_id': self.partner_id.id,
        #     'purchase_request_id': self.id,
        #     'order_line_ids': lines,
        # })
        # return {
        #     'name': 'Create Purchase Order',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'purchase.order.wizard',
        #     'view_mode': 'form',
        #     'view_id': view_id,
        #     'target': 'new',
        #     'res_id': wizard.id,
        # }
    # def compress_products(self):
    #     my_products = []
    #     product_quantity = {}
    #     for order in self.orderlines:
    #         print("first for")
    #         if order.product_id.id in product_quantity.keys():
    #             product_quantity[order.product_id.id] += order.Remaining_Quantity
    #         else:
    #             product_quantity[order.product_id.id] = order.Remaining_Quantity
    #
    #     for prod_id in product_quantity:
    #         product = self.env['product.product'].browse(prod_id)
    #         print(product)
    #         my_products.append((0, 0, {
    #             'product_id': product.id,
    #             'name': product.name,
    #             'price_unit': product.standard_price,
    #             'product_qty': product_quantity[prod_id],
    #         }))
    #         self.env['purchase.order.wizard.line'].create({
    #             'order_wizard': self.po_ids.id,
    #             'product_id': product,
    #             'prod_Quantity': product_quantity[prod_id]
    #         })

    # @api.constrains('order_line_ids.Ordered_Quantity')
    # @api.depends('order_line_ids.Ordered_Quantity')

    def _compute_remove_po(self):
        for rec in self:
            rec.remove_po = any(line.Ordered_Quantity!=line.Quantity for line in rec.orderlines)
        # for rec in self:
        #     flag=[]
        #     for product in rec.order_line_ids:
        #         print("flag = ",flag , product.Description)
        #         if product.Ordered_Quantity == product.Quantity:
        #             flag.append(1)
        #         else:
        #             flag.append(0)
        #     prod=1
        #     for l in flag:
        #         prod*=l
        #     if prod == 1:
        #         rec.remove_po=True



    #This function handels duplicated product ids in the same purchase request and put them in one line with total quantity
def merge_prod_qty(self,vals):
    product_quantity = {}
    for old_product in self.orderlines:
        product_quantity[old_product.product_id.id]= old_product.Quantity

    for order in vals[0]['orderlines']:
        if type(order[2]) is dict:
            # duplicated we gededa
            if order[2]['product_id'] in product_quantity.keys():
                product_quantity[order[2]['product_id']] += order[2]['Quantity']
            # msh duplicated bas kema gededa
            else:
                product_quantity[order[2]['product_id']] = order[2]['Quantity']

    products_in_lines = []
    # fill the product lines list with products and their total quantity
    for prod_id in product_quantity:
        product = self.env['product.product'].browse(prod_id)
        products_in_lines.append({
            'product_id': product.id,
            'Description': product.name,
            'Cost': product.standard_price,
            'pur_req_id': self,
            'Quantity': product_quantity[prod_id],
        })

    newquant = []
    for prod_id in product_quantity:
        newquant.append([0, 0, {
            'product_id': prod_id,
            'Quantity': product_quantity[prod_id],
        }])
    vals[0]['orderlines'] = newquant
    return vals

