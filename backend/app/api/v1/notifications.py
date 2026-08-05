from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for notifications /'}

@router.put('/read')
def put_read():
    return {'message': 'Mock response for notifications /read'}

