from fastapi import APIRouter

router = APIRouter()

@router.get('/config')
def get_config():
    return {'message': 'Mock response for game /config'}

@router.get('/settings')
def get_settings():
    return {'message': 'Mock response for game /settings'}

@router.put('/settings')
def put_settings():
    return {'message': 'Mock response for game /settings'}

@router.post('/start')
def post_start():
    return {'message': 'Mock response for game /start'}

@router.post('/pause')
def post_pause():
    return {'message': 'Mock response for game /pause'}

@router.post('/resume')
def post_resume():
    return {'message': 'Mock response for game /resume'}

@router.post('/finish')
def post_finish():
    return {'message': 'Mock response for game /finish'}

