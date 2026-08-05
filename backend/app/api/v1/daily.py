from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for daily /'}

@router.post('/claim')
def post_claim():
    return {'message': 'Mock response for daily /claim'}

