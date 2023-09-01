# -*- coding: utf-8 -*-
from .. import woocommerce
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import Warning,ValidationError, RedirectWarning, UserError
from odoo.http import request
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)



class Product_Product(models.Model):
    _inherit='product.template'
    
    
    def action_prepare_sync(self):
        for line in self.search([('id', '=', self.env.context.get('active_ids'))]).filtered(lambda po: po.woo_commerce_prod_to_sync ==False):
            line.write({'woo_commerce_prod_to_sync': True})
        
    
    woo_commerce_category_id=fields.Integer(related='categ_id.woo_commerce_categ_id')
    woo_commerce_prod_to_sync=fields.Boolean(string='Product to sync ')
    woo_commerce_sync_done=fields.Boolean(string='Product sync done ')
    woo_commerce_product_id=fields.Integer(string='Product Woo Commerce Id ')
    woo_commerce_id=fields.Many2one("res.config.woo",string="Instance")
    last_woo_update=fields.Datetime('Last Woo Update')
    
    
    
    def woo_product_sync(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        instance=self.woo_commerce_id
        try:
            wcapi = instance.connect_in_woo()
            
            for item in self.search([('id', 'in', self.env.context.get('active_ids'))]).filtered(lambda po: po.woo_commerce_prod_to_sync ==True):
                
                if not item.woo_commerce_id or not item.woo_commerce_category_id :
                    raise UserError(_(" Missing to synchronize the product category or to add the correspondence woo instance  ")) 
                
                
                
                if not item.woo_commerce_product_id:
                    data = {
                        "name": item.name,
                        "type": "simple",
                        "regular_price": str(item.list_price),
                        "description":item.description,
                        "stock_quantity": str(item.qty_available),
                        "sku": item.barcode or item.default_code,
                        "short_description": item.name,
                        "categories": [{"id": item.woo_commerce_category_id},],}
                    
                    res=wcapi.post("products", data).json()
                    _logger.info("payload response %s.",res)
                    if res:
                        item.woo_commerce_sync_done=True
                        item.woo_commerce_prod_to_sync=False
                        item.woo_commerce_product_id=res['id']
                        item.last_woo_update=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        continue
                        
                else:
                    data = {
                         "name": item.name,
                        "type": "simple",
                        "regular_price": str(item.list_price),
                        "stock_quantity": str(item.qty_available),
                        "sku": item.barcode or item.default_code,
                        "description":str(item.description) or '',
                        "short_description": item.name,
                            }
                    
                    res=wcapi.put("products/%s"%item.woo_commerce_product_id, data).json()
                    _logger.info("payload response %s.",res)
                    if res:
                        item.woo_commerce_sync_done=True
                        item.woo_commerce_prod_to_sync=False
                        item.last_woo_update=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        continue
        except Exception as err:
            _logger.info("Failed to connect to Woo Commerce to sync product .")
            raise UserError(_("Connection failed to sync product: %s") % tools.ustr(err))   
            return True            
    

