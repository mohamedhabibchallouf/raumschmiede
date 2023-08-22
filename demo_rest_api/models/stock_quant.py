# -*- coding: utf-8 -*-

from __future__ import division
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    value = fields.Monetary(compute='_compute_value_stock',store=True,)
    currency_id = fields.Many2one(related='product_id.currency_id',)

    @api.depends('quantity')
    def _compute_value_stock(self):
  
        # Just take into account the quants with usage internal and
        # that belong to the company
        quants_to_evaluate = self.filtered(lambda qua: qua.location_id._should_be_valued() 
                                           and not(qua.owner_id and qua.owner_id != qua.company_id.partner_id))
        #import pdb;pdb.set_trace()
        product_ids = quants_to_evaluate.mapped('product_id')
        product_valuation = dict.fromkeys(product_ids._ids, 0.0)
        product_quantity = dict.fromkeys(product_ids._ids, 0.0)

        # Get the sum of remaining value and remaining qty of the stock moves
        # with the current product. The total by product is saved in a
        # dictionary that will be used to calculate the inventory value
        # by quant
        if product_ids:
            self.env.cr.execute("""SELECT product_id,
                                COALESCE(SUM(remaining_value),0)
                                FROM stock_move WHERE remaining_value > 0
                                and product_id IN %s group by product_id;""",
                                (tuple(product_ids._ids),))
            product_valuation.update(dict(self.env.cr.fetchall()))

            self.env.cr.execute("""SELECT product_id,
                                COALESCE(SUM(remaining_qty),0)
                                FROM stock_move WHERE remaining_value > 0
                                and product_id IN %s group by product_id;""",
                                (tuple(product_ids._ids),))
            product_quantity.update(dict(self.env.cr.fetchall()))

        # For standard and avg method, the move does not save accounting
        # information (remaining qty and remaining value). For this
        # case the standard price will be used
        for product in product_ids.filtered(lambda prod:
                                            prod.cost_method != 'fifo'):
            product_valuation[product.id] = product.standard_price

        for quant in quants_to_evaluate:
            prod = quant.product_id
            quant.value = 0.0

            # There is no average value for the standard method. Then, the
            # standard price is multiplied directly by the quantity in the
            # quant
            if prod.cost_method != 'fifo':
                quant.value = product_valuation[prod.id] * quant.quantity
                continue

            # In case of FIFO, the average value of the product in the
            # moves -> sum(total_valuation) / sum(qty_on_hand), will be
            # multiplied by quantity in the quant.
            if product_quantity[prod.id] > 0:
                quant.value = (product_valuation[prod.id] /
                               product_quantity[prod.id] * quant.quantity)


