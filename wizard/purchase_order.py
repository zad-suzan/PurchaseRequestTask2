from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderWizard(models.TransientModel):
    _name = "purchase.order.wizard"
    _description = "Purchase Order"

    def _default_prod_quant(self):
        request = self.env['purchase.request'].browse(self.env.context['active_id'])
        print("aaaaaaaaaaaaaaaaaa4")
        products_in_lines = []
        for order in request.orderlines:
            print('order :', order)
            print('order iiiiiiiid:', order.id)
            products_in_lines.append({
                'pur_req_line': order.id,
                'product_id': order.product_id,
                'prod_name': order.product_id.name,  # order.Description
                'prod_Quantity': order.Quantity,
                'prod_Ordered_Quantity': order.Ordered_Quantity,
                'prod_Remaining_Quantity': order.Quantity - order.Ordered_Quantity
            })
            print('products_in_lines',products_in_lines)
        return [(0, 0, line) for line in products_in_lines]

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
    pr_sdate = fields.Date(related="purchase_request_id.StartDate")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    # ele kan 4a6al
    # order_line_ids = fields.One2many(related="purchase_request_id.orderlines", readonly=False )
    order_line_ids = fields.One2many("purchase.order.wizard.line", "order_wizard")#, default=_default_prod_quant)
    # total = fields.Float(string="Total Price", compute='_compute_new_total_price', readonly=True)
    pr_lines = fields.Many2one('purchase.request.line')
    po_lines = fields.Many2one('purchase.order.line')

    def default_get(self, fields):
        result = super(PurchaseOrderWizard, self).default_get(fields)
        result['purchase_request_id'] = self.env.context.get('active_id')
        return result

    # @api.depends('order_line_ids')
    # def _compute_new_total_price(self):
    #     for rec in self:
    #         sum = 0
    #         for order in rec.order_line_ids:
    #             sum += (order.product_id.standard_price * order.Quantity)
    #         rec.total = sum

    def create_purchase_order(self):
        self.compute_ordered_quantity()
        # for rec in self:
        #     rec.purchase_request_id.orderlines._onchange_ordered_quantity
        order_lines = []
        # qtys=[]

        for line in self.order_line_ids:
            print('line.prod_Quant_to_order',line.prod_Quant_to_order)
            print('line.pur_req_line',line.pur_req_line)
            print('line.pur_req_line.Ordered_Quantity',line.pur_req_line.Ordered_Quantity)
            line.pur_req_line.Ordered_Quantity += line.prod_Quant_to_order
            print('psssst',line.pur_req_line.Ordered_Quantity)
            # request = self.env['purchase.request.line'].browse(self.env.context['active_id'])
            # print("yayayayay", request)
            print('11111111111111111111', line.pur_req_line)
            print('122222222222222', line.pur_req_line.id)
            order_lines.append((0, 0, {
                'name': line.prod_name,
                'product_id': line.product_id.id,
                'product_qty': line.prod_Quant_to_order,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
                'price_unit': line.product_id.standard_price,
                'pur_req_line':line.pur_req_line.id,
            }))

            # 'price_unit': 1,

        print('hhhhhhhhhhhhhhhhhasd')
        print(order_lines)
        po = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': order_lines,
            'date_order': fields.Date.today(),
            'pur_req': self.purchase_request_id.id,
        })
        # self.purchase_request_id.po_count+=1
        print(order_lines)

        # for rec in self:
        #     for line in rec.po_lines:
        # #         # line.pr_lines.Ordered_Quantity = rec.order_line_ids.prod_Ordered_Quantity
        #         line.Ordered_Quantity = self.po_lines.product_qty

    def compute_ordered_quantity(self):
        # orderd = []
        for rec in self:
            for product in rec.order_line_ids:
                # if product.prod_Ordered_Quantity + product.prod_Quant_to_order <= product.prod_Quantity:
                #     product.prod_Ordered_Quantity += product.prod_Quant_to_order
                # print("abl iffffffffffffffffff", product.prod_Quant_to_order, product.prod_Remaining_Quantity)
                if product.prod_Quant_to_order <= product.prod_Remaining_Quantity:
                    # print("1111product.prod_Quant_to_order", product.prod_Quant_to_order)
                    # print("1111product.prod_Ordered_Quantity", product.prod_Ordered_Quantity)
                    # print("1111product.prod_Remaining_Quantity", product.prod_Remaining_Quantity)
                    product.prod_Ordered_Quantity += product.prod_Quant_to_order
                    product.prod_Remaining_Quantity -= product.prod_Quant_to_order
                    # print("product.prod_Remaining_Quantity", product.prod_Remaining_Quantity)
                    # print("product.prod_Ordered_Quantity", product.prod_Ordered_Quantity)
                    # orderd.append(product.prod_Ordered_Quantity)
                    # rec.pr_lines.write({
                    #     'Ordered_Quantity': product.prod_Ordered_Quantity,
                    # })
                    # print("e4at")

                else:
                    raise ValidationError("Quantity to Order can't exceed Needed Quantity")
            # index=0
            # for pl in rec.pr_lines:
            #     pl.Ordered_Quantity = orderd[index]
            #     index+=1

    #
    #
    #     def cancel(self):
    #         # On click cancel button, Just close the wizard
    #         pass
    #


class PurchaseOrderWizardLine(models.TransientModel):
    _name = "purchase.order.wizard.line"
    _description = "Purchase Order Line"

    order_wizard = fields.Many2one("purchase.order.wizard")
    pur_req_line = fields.Many2one('purchase.request.line',store=True)
    product_id = fields.Many2one("product.product", readonly=True)
    prod_name = fields.Char(string="Product", readonly=True)
    prod_Quantity = fields.Float(readonly=True)
    prod_Ordered_Quantity = fields.Float(string="Ordered Quantity", readonly=True)  # ,
    # default=0,compute='_compute_ordered_quantity')
    prod_Remaining_Quantity = fields.Float(string="Remaining Quantity")  # ,compute='_compute_remaining_quantity')
    prod_Quant_to_order = fields.Float(string="Quantity To Order")

    # @api.depends('prod_Ordered_Quantity')
    # def _compute_remaining_quantity(self):
    #     for rec in self:
    #         rec.prod_Remaining_Quantity = rec.prod_Quantity - rec.prod_Ordered_Quantity
    # @api.depends("prod_Quant_to_order")
    def _compute_remaining_quantity(self):
        for rec in self:
            # for product in rec.order_line_ids:
            # if product.prod_Ordered_Quantity + product.prod_Quant_to_order <= product.prod_Quantity:
            #     product.prod_Ordered_Quantity += product.prod_Quant_to_order
            if rec.prod_Quant_to_order <= rec.prod_Remaining_Quantity:
                print("1111product.prod_Quant_to_order", rec.prod_Quant_to_order)
                print("1111product.prod_Ordered_Quantity", rec.prod_Ordered_Quantity)
                print("1111product.prod_Remaining_Quantity", rec.prod_Remaining_Quantity)
                rec.prod_Ordered_Quantity += rec.prod_Quant_to_order
                rec.prod_Remaining_Quantity -= rec.prod_Quant_to_order
                print("product.prod_Remaining_Quantity", rec.prod_Remaining_Quantity)
                print("product.prod_Ordered_Quantity", rec.prod_Ordered_Quantity)


            else:
                raise ValidationError("Quantity to Order can't exceed Needed Quantity")
