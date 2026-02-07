import pytest
from sqlalchemy.exc import IntegrityError
from models.user import User, UserRole
from models.department import Department

def test_create_valid_user(db_session):
    """Test creating a valid user"""
    user = User(
        student_id="S12345",
        email="student@test.com",
        password_hash="hashed_password",
        name="Test Student"
    )
    db_session.add(user)
    db_session.commit()

    # Assert
    assert user.id is not None
    assert user.student_id == "S12345"
    assert user.role == UserRole.STUDENT
    assert user.created_at is not None

def test_user_defaults(db_session):
    """Test user default values"""
    user = User(
        student_id="S12345",
        email="student@test.com",
        password_hash="hashed_password",
        name="Test Student"
    )
    db_session.add(user)
    db_session.commit()

    assert user.role == UserRole.STUDENT
    assert user.created_at is not None

def test_unique_email(db_session):
    """Test email uniqueness constraint"""
    user1 = User(
        student_id="S1",
        email="duplicate@test.com",
        password_hash="pw1",
        name="User 1"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        student_id="S2",
        email="duplicate@test.com",  # Duplicate email
        password_hash="pw2",
        name="User 2"
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_unique_student_id(db_session):
    """Test student_id uniqueness constraint"""
    user1 = User(
        student_id="DUPLICATE_ID",
        email="email1@test.com",
        password_hash="pw1",
        name="User 1"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        student_id="DUPLICATE_ID",  # Duplicate student_id
        email="email2@test.com",
        password_hash="pw2",
        name="User 2"
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_create_admin_user(db_session):
    """Test creating an admin user"""
    admin = User(
        student_id="ADMIN1",
        email="admin@test.com",
        password_hash="admin_pw",
        name="Admin User",
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()

    assert admin.role == UserRole.ADMIN

def test_nullable_department_id(db_session):
    """Test that department_id can be null"""
    user = User(
        student_id="S12345",
        email="student@test.com",
        password_hash="hashed_password",
        name="Test Student",
        department_id=None
    )
    db_session.add(user)
    db_session.commit()

    assert user.department_id is None

def test_user_department_relationship(db_session):
    """Test user-department relationship"""
    dept = Department(
        code="CSE",
        name="Computer Science"
    )
    db_session.add(dept)
    db_session.commit()

    user = User(
        student_id="S_CSE",
        email="cse@test.com",
        password_hash="pw",
        name="CSE Student",
        department_id=dept.id
    )
    db_session.add(user)
    db_session.commit()

    assert user.department == dept
    assert user.department.code == "CSE"
    assert user in dept.users
