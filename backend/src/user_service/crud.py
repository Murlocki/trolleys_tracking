# Crud юзеров
from datetime import datetime

from sqlalchemy import select, and_, desc, asc, cast, String, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.shared import logger_setup
from src.user_service.auth_functions import get_password_hash, verify_password
from src.user_service.models import User, Role, UserData
from src.user_service.schemas import UserCreate, UserUpdate, PasswordForm

logger = logger_setup.setup_logger(__name__)


# CRUD операции с пользователями
async def create_user(db: AsyncSession, user: UserCreate):
    user_password_hash = get_password_hash(user.password)
    user_data = user.user_data
    db_user = User(
        username=user.username,
        hashed_password=user_password_hash,
        is_active=True,
        role=user.role
    )
    logger.info(f"User create data {db_user}")
    async with db.begin():
        db.add(db_user)
        if user.role != Role.SERVICE:
            user_data = UserData(
                first_name=user.user_data.first_name,
                last_name=user.user_data.last_name,
                email=user.user_data.email,
                user=db_user
            )
            db.add(user_data)
    await db.refresh(db_user)
    logger.info(f"User created {db_user}")
    logger.info(f"User data created {user_data}")
    await db.refresh(db_user)
    return db_user

async def search_users(
    db: AsyncSession,
    filters: dict,
    sort_by: list[str] = None,
    sort_order: list[str] = None,
    page: int = 1,
    count: int = 10
):
    stmt = select(User).outerjoin(User.user_data).options(joinedload(User.user_data))

    field_column_map = {
        "username": User.username,
        "email": UserData.email,
        "first_name": UserData.first_name,
        "last_name": UserData.last_name,
        "role": User.role,
        "id": User.id,
        "created_at": User.created_at,
        "updated_at": User.updated_at,
    }

    # Фильтрация
    conditions = []
    for field, value in filters.items():
        if value is None:
            continue

        if field == "created_from" and value is not None:
            conditions.append(User.created_at >= value)
        elif field == "created_to" and value is not None:
            conditions.append(User.created_at <= value)
        elif field == "updated_from" and value is not None:
            conditions.append(User.updated_at >= value)
        elif field == "updated_to" and value is not None:
            conditions.append(User.updated_at <= value)
        elif field == "role":
            conditions.append(cast(User.role, String).ilike(f"%{value}%"))
        elif field in field_column_map:
            column = field_column_map[field]
            conditions.append(column.ilike(f"%{value}%"))

    if conditions:
        stmt = stmt.where(*conditions)

    # Сортировка
    order_clauses = []
    if sort_by:
        for i, field_name in enumerate(sort_by):
            column = field_column_map.get(field_name)
            if not column:
                continue
            order = sort_order[i] if i < len(sort_order) else "asc"
            order_clauses.append(desc(column) if order.lower() == "desc" else asc(column))
    if order_clauses:
        stmt = stmt.order_by(*order_clauses)

    result = await db.execute(stmt.offset((page-1) * count).limit(count))
    return result.scalars().all()





async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    """
    Обновляет данные пользователя, включая вложенные модели

    Args:
        db: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя (целое число)
        user_update: Данные для обновления (Pydantic модель)

    Returns:
        Обновленный объект User или None если пользователь не найден
    """
    try:
        # Получаем пользователя с joined user_data
        result = await db.execute(
            select(User)
            .options(joinedload(User.user_data))
            .filter(User.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            logger.error(f"User {user_id} not found")
            return None
        logger.info(f"User found {db_user.to_dict()}")
        # Конвертируем Pydantic модель в словарь
        update_data = user_update.model_dump(exclude_unset=True)
        logger.info(f"User update data {update_data}")
        db_user = await update_user_data(db=db, db_user=db_user, user_update=user_update)
        logger.info(f"User update user_data {db_user.to_dict()}")
        # Обновляем основные поля пользователя
        for key, value in update_data.items():
            if hasattr(db_user, key) and key!="user_data":
                setattr(db_user, key, value)
        db_user.updated_at = datetime.now()
        logger.info(f"User updated {db_user.to_dict()}")
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}", exc_info=True)
        raise

async def update_user_password(db: AsyncSession, user_id: int, password_form: PasswordForm) -> User | None:
    result = await db.execute(
        select(User)
        .options(joinedload(User.user_data))
        .filter(User.id == user_id)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        logger.error(f"User {user_id} not found")
        return None
    db_user.hashed_password = get_password_hash(password=password_form.new_password)
    db_user.version = password_form.user_version + 1
    db_user.updated_at = datetime.now()
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user_data(db: AsyncSession, db_user: User, user_update: UserUpdate) -> User | None:
    if user_update.role == Role.SERVICE:
        if db_user.user_data is not None:
            result = await db.delete(db_user.user_data)
            await db.commit()
            await db.refresh(db_user)
        return db_user
    if db_user.user_data is None:
        db.add(UserData(user=db_user,**user_update.user_data.model_dump(exclude_unset=True)))
        await db.commit()
        await db.refresh(db_user)
        return db_user

    for key, value in user_update.user_data.model_dump(exclude_unset=True).items():
        if hasattr(db_user.user_data, key):
            setattr(db_user.user_data, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: int):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.id == user_id))
        db_user = db_user.scalar()
        if db_user is None:
            logger.error(f"User {user_id} not found.")
            return None
        logger.info(f"Found user {db_user.to_dict()}")
        return db_user

async def delete_user(db: AsyncSession, user: User):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == user.username))
        db_user = result.scalar_one_or_none()
        if not db_user:
            logger.warning(f"User {user.username} not found.")
            return None
        logger.info(f"Deleted user {db_user.to_dict()}")
        await db.delete(db_user)
    return db_user

async def get_user_count(db: AsyncSession)->int:
    async with db.begin():
        result = await db.execute(select(func.count(User.id)))
    return result.scalar()


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        db_user = await db.execute(
            select(User)
            .join(User.user_data)  # Явное соединение
            .where(
                and_(
                    User.role.in_([Role.ADMIN, Role.SUPER_ADMIN]),
                    UserData.email == email  # Прямое обращение к связанной таблице
                )
            )
        )
        db_user = db_user.scalar_one_or_none()
        logger.info(f"Found user {db_user}")
        return db_user


async def get_user_by_username(db: AsyncSession, username: str):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.username == username))
        db_user = db_user.scalar_one_or_none()
        logger.info(f"Found user {db_user}")
        return db_user


async def get_users(db: AsyncSession):
    async with db as session:
        result = await session.execute(select(User))
        result = result.scalars().all()
        logger.info(f"Found users {result}")
        return result


async def authenticate_user(db: AsyncSession, identifier: str, password: str):
    user = await get_user_by_email(db, identifier) or await get_user_by_username(db, identifier)
    if not user:
        logger.error(f"User {identifier} not found.")
        return None
    if not verify_password(password, user.hashed_password):
        logger.error(f"User {identifier} dont have correct password.")
        return None
    logger.info(f"Authenticated user {user.to_dict()}")
    return user
