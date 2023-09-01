# -*- coding: utf-8 -*-
from .. import woocommerce
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError,Warning

import logging
_logger = logging.getLogger(__name__)




class woo_instance_config(models.Model):
    _name = 'res.config.woo'
    _description = "WooCommerce Instance"

   

    name = fields.Char("Instance Name")
    consumer_key=fields.Char("Consumer Key",required=True,help="Login into WooCommerce site,Go to Admin Panel >> WooCommerce >> Settings >> API >> Keys/Apps >> Click on Add Key")
    consumer_secret=fields.Char("Consumer Secret",required=True,help="Login into WooCommerce site,Go to Admin Panel >> WooCommerce >> Settings >> API >> Keys/Apps >> Click on Add Key")    
    host=fields.Char("Host",required=True)
    verify_ssl=fields.Boolean("Verify SSL",default=False,help="Check this if your WooCommerce site is using SSL certificate")
    woo_version = fields.Selection([('new','2.6+'),('old','<=2.6')],default='old',string="WooCommerce Version",help="Set the appropriate WooCommerce Version you are using currently or\nLogin into WooCommerce site,Go to Admin Panel >> Plugins")    
    is_latest=fields.Boolean('3.0 or later',default=False)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ],  default='draft')
    
    
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this instance")
    
    category_count = fields.Integer(
        '# Categories', compute='_compute_category_count',
        help="The number of Categories under this instance ")


    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('woo_commerce_sync_done', '=', True),('woo_commerce_id', '=', self.id)], ['woo_commerce_sync_done'], ['woo_commerce_sync_done'])
        group_data = dict(('count', data['woo_commerce_sync_done_count']) for data in read_group_res)
        self.product_count = group_data.get('count', 0)
        
    def _compute_category_count(self):
        read_group_res = self.env['product.category'].read_group([('woo_commerce_categ_sync_done', '=', True),('woo_commerce_id', '=', self.id)], ['woo_commerce_categ_sync_done'], ['woo_commerce_categ_sync_done'])
        group_data = dict(('count', data['woo_commerce_categ_sync_done_count']) for data in read_group_res)
        self.category_count = group_data.get('count', 0)


  

    @api.constrains('host')
    def woo_host_constrains(self):
        if self.host and self.host.strip()[-1] == '/':
            raise Warning(
                "Host should not end with character '/'.\nPlease Remove it from the end of host string and try again.")

    @api.onchange('host')
    def onchange_host(self):
        if self.host and 'https' in self.host:
            self.verify_ssl = True
        else:
            self.verify_ssl = False
    
    
    def test_woo_connection(self):
   
        host = self.host
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        wp_api = True if self.woo_version == 'new' else False
        version = "wc/v1" if wp_api else "v3"
        if self.is_latest:
            version = "wc/v2"
        wcapi = woocommerce.api.API(url=host, consumer_key=consumer_key,
                    consumer_secret=consumer_secret,verify_ssl=self.verify_ssl,wp_api=wp_api,version=version,query_string_auth=True)  
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))
        else:
            self.state='confirmed'
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
    
    def connect_in_woo(self):
        host = self.host
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        wp_api = True if self.woo_version == 'new' else False
        version = "wc/v1" if wp_api else "v3"
        if self.is_latest:
            version = "wc/v2"
        try:
            wcapi = woocommerce.api.API(url=host, consumer_key=consumer_key,
                        consumer_secret=consumer_secret,verify_ssl=self.verify_ssl,wp_api=wp_api,version=version,query_string_auth=True)
            return wcapi
        except Exception as err:
                _logger.info("Failed to connect to Woo Commerce .")
                raise UserError(_("Connection failed: %s") % tools.ustr(err))   
        return True
    
    
    
    def sync_woo_product_to_odoo(self):
        wcapi = self.connect_in_woo()
        products=wcapi.get("products").json()
        for product in products:
            if self.env['product.template'].search([('name','=',product['name'])]):
                continue
            else:
                self.env['product.template'].create({'name':product['name'],
                                                     'woo_commerce_product_id':product['id'],
                                                     'woo_commerce_id':self.id,
                                                     'list_price':product['regular_price'],
                                                     'woo_commerce_sync_done':True,
                                                     'detailed_type':'product',
                                                     'last_woo_update':datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                                                     'categ_id':self.env['product.category'].search([('name','=',product['categories'][0]['name'])],limit=1).id})
        return True
    
    
    def sync_woo_categ_to_odoo(self):
        wcapi = self.connect_in_woo()
        categories=wcapi.get("products/categories").json()
        for categ in categories:
            #import pdb;pdb.set_trace()
            if self.env['product.category'].search([('name','=',categ['name'])]):
                continue
            else:
                self.env['product.category'].create({'name':categ['name'],
                                                     'woo_commerce_categ_id':categ['id'],
                                                     'woo_commerce_id':self.id,
                                                     'last_woo_update':datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
        
        return True
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
