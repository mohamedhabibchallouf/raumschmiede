# -*- coding: utf-8 -*-x
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

#===============================================================================
# for Auth please collect the session id
# http://server_ip/web/session/authenticate
# Body: {"jsonrpc": "2.0","params": {"db":"dbname","login":"admin","password":"admin"}}
# header:content-type: application/json
#===============================================================================


class AirdropAPI(http.Controller):

    # Sample Controller Created

    #===========================================================================
    # Get : list of Products available 
    #===========================================================================
    
    @http.route('/api/articles', type='json', auth='user')
    def get_articles(self):
        
        product_rec = request.env['product.product'].search([])
        products = []
        for rec in product_rec:
            
            vals = {
                'id': rec.id,
                'name': rec.name,
                'description': rec.description,
            }
            products.append(vals)
        
        data = {'status': 200, 'response': products, 'message': 'Done All Products Returned'}
        return data
    #===========================================================================
    # Get : recieve a details for specific product
    #===========================================================================
    
    @http.route('/api/article/<string:id>', type='json', auth='user')
    def get_article_id(self, **rec):
        if request.jsonrequest:
            if rec['id']:
                product = request.env['product.product'].sudo().search([('id', '=', rec['id'])])
                print("rec...", rec)
                products = []
                for rec in product:
                    vals = {
                        'id': rec.id,
                        'name': rec.name,
                        'description': rec.description,
                    }
                    products.append(vals)
        data = {'status': 200, 'response': products, 'message': 'Done'}
        return data
    
    #===========================================================================
    # Post : create new product  based on name and code
    #===========================================================================
    
    @http.route('/api/create_article', type='json', auth='user')
    def create_article(self, **rec):
        if request.jsonrequest:
            if rec['name']:
                vals = {
                    'name': rec['name'],
                    'default_code': rec['code']
                }
                new_product = request.env['product.product'].sudo().create(vals)
                args = {'success': True, 'message': 'Success', 'id': new_product.id}
        return args
    
    #===========================================================================
    # Put:  product by passing the param as argment
    #{"jsonrpc": "2.0","params": {"id":"3","name":"Airdrop","default_code":"002"}}
    #===========================================================================
    @http.route('/api/update_article', type='json', auth='user')
    def update_article(self, **rec):
        if request.jsonrequest:
                import pdb;pdb.set_trace()
                product = request.env['product.product'].sudo().search([('id', '=', rec['id'])])
                if product:
                    product.sudo().write(rec)
                args = {'success': True, 'message': 'product Updated'}
        return args
        
    
    #===========================================================================
    # Delete: delete product by passing the Id as argment
    #===========================================================================
    @http.route('/api/delete_article', type='json', auth='user')
    def delete_article(self, **rec):
        if request.jsonrequest:
                product = request.env['product.product'].sudo().search([('id', '=', rec['id'])])
                for rec in product:
                    rec.unlink()
                args = {'success': True, 'message': 'Deleted', 'id': product.id}
        return args
    
    
    #===========================================================================
    # Get: Retrieve the list of shelfs or location available 
    #===========================================================================
    @http.route('/api/shelfs', type='json', auth='user')
    def get_shelfs(self):
        product_rec = request.env['stock.location'].search([('usage','=','internal')])
        products = []
        for rec in product_rec:
            vals = {
                'id': rec.id,
                'row': rec.posx,
                'bay': rec.posy,
            }
            products.append(vals)
        data = {'status': 200, 'response': products, 'message': 'Done All shelfs Returned'}
        return data
    
    #===========================================================================
    # Get: Retrieve all the stock available  
    #===========================================================================
    @http.route('/api/warehouse', type='json', auth='user')
    def get_shelfs_value(self):
        if request.jsonrequest:
                product_rec = request.env['stock.quant'].search([])
                products = []
                for rec in product_rec:
                    vals = {
                        'id': rec.product_id.id,
                        'name': rec.product_id.name,
                        'amount': rec.value,
                    }
                    products.append(vals)
                data = {'status': 200, 'response': products, 'message': 'Done All Products Values Returned'}
        return data
    
    
    #===========================================================================
    # GET : Retrieve  the list of Goods based on Row and Bay for specific product  
    # example :http://mc86-laptop:9112/api/warehouse/1&1&3
    #===========================================================================
    @http.route('/api/warehouse/<string:row>&<string:bay>&<string:id>', type='json', auth='user')
    def get_shelfs_value_row_by_product(self,**rec):
        if request.jsonrequest:
                posx=rec['row']
                posy=rec['bay']
                product_id=request.env['product.product'].search([('id','=',rec['id'])])
                domain=['&',('posx','=',posx),('posy','=',posy)]
                #domain=[('posx','=',1)]
                location_id=request.env['stock.location'].search(domain)
                domain=['&',('location_id','in',[location_id.id]),('product_id','=',product_id.id)]
                product_rec = request.env['stock.quant'].search(domain)
                products = []
                for rec in product_rec:
                    vals = {
                        'id': rec.product_id.id,
                        'name': rec.product_id.name,
                        'amount': rec.value,
                        'row':posx,
                        'bay':posy,
                    }
                    products.append(vals)
                data = {'status': 200, 'response': products, 'message': 'Done All Products Returned'}
        return data
    
    #===========================================================================
    # GET : Retrieve  the list of Goods for specific Row 
    # example :http://mc86-laptop:9112/api/warehouse/pick/18&20&1&2
    #===========================================================================
    @http.route('/api/warehouse/<string:row>', type='json', auth='user')
    def get_shelfs_quantity_row(self,**rec):
        if request.jsonrequest:
                posx=rec['row']
                domain=[('posx','=',posx),]
                location_id=request.env['stock.location'].search(domain).mapped('id')
                domain=[('location_id','in',location_id)]
                product_rec = request.env['stock.quant'].search(domain)
                products = []
                for rec in product_rec:
                    vals = {
                        'id': rec.product_id.id,
                        'name': rec.product_id.name,
                        'quantity': rec.quantity,
                        'row':posx,
                        'bay':rec.location_id.posy,
                    }
                    products.append(vals)
                data = {'status': 200, 'response': products, 'message': 'Done All Products Returned'}
        return data
    
    
    #===========================================================================
    # POST : Create draft stock internal picking 
    # example :http://mc86-laptop:9112/api/warehouse/pick/18&20&1&2
    #===========================================================================
    @http.route('/api/warehouse/pick/<string:from>&<string:to>&<string:qty>&<string:id>', type='json', auth='user')
    def pick_product(self,**rec):
        if request.jsonrequest:
            
                location_from=rec['from']
                location_to=rec['to']
                domain_from=[('id','=',location_from),]
                domain_to=[('id','=',location_to),]
                
                location_from_id=request.env['stock.location'].search(domain_from).mapped('id')
                location_to_id=request.env['stock.location'].search(domain_to).mapped('id')
                
                product_id=request.env['product.product'].search([('id','=',rec['id'])])
                domain=['&',('location_id','in',location_from_id),('product_id','=',product_id.id)]
                product_rec = request.env['stock.quant'].search(domain)
                
                products=[]
                stock_picking=request.env['stock.picking']
                stock_move=request.env['stock.move']
                picking_type_id=request.env['stock.picking.type'].search([('code','=','internal')],limit=1)
                
                if product_rec:
                    for line in product_rec:
                        val_picking={
                            'location_dest_id': location_to_id[0],
                            'location_id': location_from_id[0],
                            'picking_type_id':picking_type_id.id
                            
                            }
                    picking_id=stock_picking.sudo().create(val_picking)
                    if picking_id:
                        for line in product_rec:    
                            vals = {
                                'name':'Airdrop-Json',
                                'product_id': line.product_id.id,
                                'location_id': location_from_id[0],
                                'product_uom_qty':  rec['qty'],
                                'location_dest_id': location_to_id[0],
                                'date':datetime.today(),
                                'product_uom':line.product_id.uom_id.id,
                                'picking_id':picking_id.id
                                
                            }
                            products.append(vals)
                        move_id=stock_move.sudo().create(vals)
                data = {'status': 200, 'response': products, 'message': 'Done All Products Returned'}
        return data

    
    
    
    
    
    
    
