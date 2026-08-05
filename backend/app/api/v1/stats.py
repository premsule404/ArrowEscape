from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for stats /'}

@router.get('/history')
def get_history():
    return {'message': 'Mock response for stats /history'}

