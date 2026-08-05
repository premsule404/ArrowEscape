from fastapi import APIRouter

router = APIRouter()

@router.get('/items')
def get_items():
    return {'message': 'Mock response for shop /items'}

@router.post('/purchase')
def post_purchase():
    return {'message': 'Mock response for shop /purchase'}

