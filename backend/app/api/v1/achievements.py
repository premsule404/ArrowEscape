from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for achievements /'}

@router.post('/unlock')
def post_unlock():
    return {'message': 'Mock response for achievements /unlock'}

