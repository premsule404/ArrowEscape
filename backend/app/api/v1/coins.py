from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_root():
    return {'message': 'Mock response for coins /'}

@router.post('/reward')
def post_reward():
    return {'message': 'Mock response for coins /reward'}

@router.post('/spend')
def post_spend():
    return {'message': 'Mock response for coins /spend'}

