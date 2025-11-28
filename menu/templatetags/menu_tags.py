from django import template
from django.db import OperationalError
from menu.models import MenuItem

register = template.Library()


@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    request = context.get('request')
    current_url = request.path if request else ''
    
    try:
        all_items = list(
            MenuItem.objects
            .filter(menu__name=menu_name)
            .select_related('parent', 'menu')
            .order_by('order', 'title')
        )
    except OperationalError:
        return {'menu_items': [], 'current_url': current_url}
    
    if not all_items:
        return {'menu_items': [], 'current_url': current_url}
    
    menu_items = build_menu_tree(all_items, current_url)
    
    return {
        'menu_items': menu_items,
        'current_url': current_url,
    }


def build_menu_tree(items, current_url):
    items_dict = {item.id: item for item in items}
    
    children_dict = {}
    root_items = []
    
    for item in items:
        if item.parent_id:
            if item.parent_id not in children_dict:
                children_dict[item.parent_id] = []
            children_dict[item.parent_id].append(item)
        else:
            root_items.append(item)
    
    active_item_id = None
    exact_match_id = None
    longest_match_length = 0
    
    for item in items:
        item_url = item.get_url()
        if not item_url or item_url == '#':
            continue
        
        normalized_item_url = item_url.rstrip('/')
        normalized_current_url = current_url.rstrip('/')
            
        if normalized_current_url == normalized_item_url or current_url == item_url:
            exact_match_id = item.id
            break
        elif (current_url.startswith(item_url) and 
              len(item_url) > longest_match_length and 
              (len(item_url) > 1 or item_url == '/')):
            active_item_id = item.id
            longest_match_length = len(item_url)
    
    if exact_match_id:
        active_item_id = exact_match_id
    
    active_path = set()
    if active_item_id:
        item_id = active_item_id
        while item_id:
            active_path.add(item_id)
            item = items_dict.get(item_id)
            if item and item.parent_id:
                item_id = item.parent_id
            else:
                break
    
    def build_tree(item_list, level=0):
        result = []
        for item in sorted(item_list, key=lambda x: (x.order, x.title)):
            is_active = item.id == active_item_id
            is_in_path = item.id in active_path
            
            item_dict = {
                'item': item,
                'children': [],
                'is_active': is_active,
                'is_expanded': False,
                'level': level,
            }
            
            if is_in_path:
                item_dict['is_expanded'] = True
            
            if is_active:
                item_dict['is_expanded'] = True
            
            if item.id in children_dict:
                children = build_tree(children_dict[item.id], level + 1)
                item_dict['children'] = children
                
                if any(child['is_active'] or child.get('has_active_children', False) for child in children):
                    item_dict['is_expanded'] = True
                    item_dict['has_active_children'] = True
                
                if level == 0 and children:
                    item_dict['is_expanded'] = True
            
            result.append(item_dict)
        
        return result
    
    return build_tree(root_items)
