from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, UserProfile, UnfinishedActivity
from app.memory.memory_manager import MemoryManager
from app.schemas.pydantic_models import UnfinishedActivitySchema

def test_memory_crud():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Add user
    user = UserProfile(name="Test Student", email="test@student.edu")
    db.add(user)
    db.commit()

    manager = MemoryManager(db)
    act = UnfinishedActivitySchema(
        user_id=user.id,
        title="Test PDF Paper",
        source_type="PDF",
        progress_percent=40.0,
        priority_score=80.0
    )
    saved = manager.add_or_update_unfinished_activity(act)
    assert saved.id is not None
    assert saved.title == "Test PDF Paper"

    retrieved = manager.get_unfinished_activities(user_id=user.id)
    assert len(retrieved) == 1
    assert retrieved[0].priority_score == 80.0
    db.close()
