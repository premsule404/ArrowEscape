from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for themes /'}

@router.post('/unlock')
def post_unlock():
    return {'message': 'Mock response for themes /unlock'}

@router.put('/equip')
def put_equip():
    return {'message': 'Mock response for themes /equip'}

