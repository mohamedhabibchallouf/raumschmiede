# -*- coding: utf-8 -*-
from odoo  import models,fields

class woo_transaction_log(models.Model):
    _name="woo.log"
    _order='id desc'
    _rec_name = 'create_date'
    _description = "WooCommerce logs"
    create_date=fields.Datetime("Create Date")
    mismatch_details=fields.Boolean("Mismatch Details")
    message=fields.Text("Message")
    type=fields.Selection([('product','Product'),('stock','Stock'),
                           ('category','Category'),('system_status','System Status')],string="Type")
    woo_instance_id=fields.Many2one("res.config.woo",string="Instance")