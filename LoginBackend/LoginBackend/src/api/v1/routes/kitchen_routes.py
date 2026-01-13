from flask import Blueprint, request, jsonify
from ...middleware.auth_middleware import token_required, roles_required
from ....infrastructure.database.session import db
from ....infrastructure.database.models import OrderModel, UserModel
from datetime import datetime
import json

kitchen_bp = Blueprint('kitchen', __name__, url_prefix='/api/v1/kitchen')

@kitchen_bp.route('/orders', methods=['POST'])
@roles_required('admin', 'restaurant_staff')
def create_order():
    try:
        data = request.get_json()
        
        if not data.get('items'):
            return jsonify({'success': False, 'error': 'Items are required'}), 400
        
        today = datetime.now().strftime("%Y%m%d")
        last_order = OrderModel.query.filter(
            OrderModel.order_number.like(f'{today}%')
        ).order_by(OrderModel.id.desc()).first()
        
        if last_order:
            last_num = int(last_order.order_number[-4:])
            new_num = f'{today}{last_num + 1:04d}'
        else:
            new_num = f'{today}0001'
        
        new_order = OrderModel(
            order_number=new_num,
            customer_name=data.get('customer_name', 'Walk-in Customer'),
            table_number=data.get('table_number', 'Takeaway'),
            items=json.dumps(data.get('items', [])),
            total_amount=data.get('total_amount', 0),
            kitchen_notes=data.get('kitchen_notes', ''),
            created_by=request.user_id,
            status='pending'
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': new_order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/orders', methods=['GET'])
@roles_required('admin', 'restaurant_staff')
def get_orders():
    try:
        status = request.args.get('status')
        today_only = request.args.get('today', 'false').lower() == 'true'
        
        query = OrderModel.query
        
        if status:
            query = query.filter_by(status=status)
        
        if today_only:
            query = query.filter(
                db.func.date(OrderModel.created_at) == datetime.now().date()
            )
        
        orders = query.order_by(OrderModel.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/orders/pending', methods=['GET'])
@roles_required('admin', 'restaurant_staff')
def get_pending_orders():
    try:
        orders = OrderModel.query.filter_by(status='pending')\
            .order_by(OrderModel.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/orders/<int:order_id>', methods=['GET'])
@roles_required('admin', 'restaurant_staff')
def get_order(order_id):
    try:
        order = OrderModel.query.get(order_id)
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@roles_required('admin', 'restaurant_staff')
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'preparing', 'ready', 'served', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False, 
                'error': f'Status must be one of: {valid_statuses}'
            }), 400
        
        order = OrderModel.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        old_status = order.status
        order.status = new_status
        
        if new_status == 'preparing':
            order.assigned_to = request.user_id
        
        if new_status in ['cancelled', 'served']:
            order.assigned_to = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Order status updated from {old_status} to {new_status}',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@kitchen_bp.route('/orders/<int:order_id>', methods=['PUT'])
@roles_required('admin', 'restaurant_staff')
def update_order(order_id):
    try:
        data = request.get_json()
        order = OrderModel.query.get(order_id)
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        if 'table_number' in data:
            order.table_number = data['table_number']
        if 'kitchen_notes' in data:
            order.kitchen_notes = data['kitchen_notes']
        if 'items' in data:
            order.items = json.dumps(data['items'])
        if 'total_amount' in data:
            order.total_amount = data['total_amount']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order updated successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@roles_required('admin')
def delete_order(order_id):
    try:
        order = OrderModel.query.get(order_id)
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@kitchen_bp.route('/dashboard', methods=['GET'])
@roles_required('admin', 'restaurant_staff')
def kitchen_dashboard():
    try:
        today = datetime.now().date()
        
        total_orders = OrderModel.query.count()
        pending_orders = OrderModel.query.filter_by(status='pending').count()
        preparing_orders = OrderModel.query.filter_by(status='preparing').count()
        ready_orders = OrderModel.query.filter_by(status='ready').count()
        
        today_orders = OrderModel.query.filter(
            db.func.date(OrderModel.created_at) == today
        ).count()
        
        today_revenue_result = db.session.query(
            db.func.sum(OrderModel.total_amount)
        ).filter(
            db.func.date(OrderModel.created_at) == today,
            OrderModel.status != 'cancelled'
        ).first()
        
        today_revenue = float(today_revenue_result[0] or 0)
        
        recent_orders = OrderModel.query\
            .order_by(OrderModel.created_at.desc())\
            .limit(10)\
            .all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'preparing_orders': preparing_orders,
                'ready_orders': ready_orders,
                'today_orders': today_orders,
                'today_revenue': today_revenue
            },
            'recent_orders': [order.to_dict() for order in recent_orders]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500