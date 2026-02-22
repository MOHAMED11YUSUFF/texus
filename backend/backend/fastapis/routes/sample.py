from fastapi import APIRouter

router = APIRouter(
    prefix="/sample",
    tags=["Sample"]
)

@router.get("/")
async def test():
    return {"message": "FastAPI is working 🚀"}