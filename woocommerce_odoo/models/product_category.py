# -*- coding: utf-8 -*-
from .. import woocommerce
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import Warning,ValidationError, RedirectWarning, UserError
from odoo.http import request
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)






class Product_Category(models.Model):
    _inherit='product.category'
    
    def action_prepare_category_to_sync(self):
        for line in self.search([('id', '=', self.env.context.get('active_ids'))]).filtered(lambda po: po.woo_commerce_categ_to_sync ==False):
            line.write({'woo_commerce_categ_to_sync': True})
        
    
    
    woo_commerce_categ_to_sync=fields.Boolean(string='Category to Sycronise ')
    woo_commerce_categ_sync_done=fields.Boolean(string='Category Syncronised Done  ')
    woo_commerce_categ_id=fields.Integer('Woo Ressouce Id')
    woo_commerce_id=fields.Many2one("res.config.woo",string="Instance")
    last_woo_update=fields.Datetime('Last Woo Update')
    
    
    def woo_category_sync(self):
        instance=self.woo_commerce_id
        transaction_log_obj=self.env['woo.transaction.log']
        try:  
            wcapi = instance.connect_in_woo()
            for categ in self.search([('id', 'in', self.env.context.get('active_ids'))]).filtered(lambda ct: ct.woo_commerce_categ_to_sync ==True):
                data = {
                            "name": categ.name,
                        }
                
                if not categ.woo_commerce_categ_id:
                    res=wcapi.post("products/categories", data).json()
                    print(res)
                    transaction_log_obj.create({'message': "create  categories \nResponse  :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'category',
                                             'woo_instance_id':instance.id
                                            })
                    #{'code': 'term_exists', 'message': 'A term with the name provided already exists with this parent.', 'data': {'status': 400, 'resource_id': 20}}
                    if res  and 'id' in res:
                        categ.woo_commerce_categ_sync_done=True
                        categ.woo_commerce_categ_to_sync=False
                        categ.woo_commerce_categ_id=res['id']
                        categ.last_woo_update=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        transaction_log_obj.create({'message': "create  categories \nResponse  not in format:: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'category',
                                             'woo_instance_id':instance.id
                                            })
                        
                if categ.woo_commerce_categ_id:
                    
                    data = {
                            "description": categ.name,
                          
                        }
                    res=wcapi.put("products/categories/%s"%categ.woo_commerce_categ_id, data).json()
               
                    if res and 'id' in res:
                        categ.woo_commerce_categ_sync_done=True
                        categ.woo_commerce_categ_to_sync=False
                        categ.last_woo_update=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        #self.woo_commerce_categ_id=res['id']
                        #self.last_update=fields.today
                        transaction_log_obj.create({'message': "Update  Categories \nResponse :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'category',
                                             'woo_instance_id':instance.id
                                            })
                    else:
                        transaction_log_obj.create({'message': "Update  Categories \nResponse Issue:: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'category',
                                             'woo_instance_id':instance.id
                                            })
        except Exception as err:
            _logger.info("Failed to connect to Woo Commerce to sync product .")
            raise UserError(_("Connection failed to sync product: %s") % tools.ustr(err))   
            return True    
            



                
            
                
                
                
                