def cart_count(request):
    return {'cart_count': len(request.session.get('cart', []))}
