from datetime import datetime

from sqlalchemy import select, desc, asc, cast, String, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.camera_service.schemas import CameraGroupSchema, CameraSchema, CameraUserAssociationAdminDTO
from src.shared.logger_setup import setup_logger
from src.shared.models import CameraGroup, Camera, CameraUserAssociation, User

logger = setup_logger(__name__)


async def create_camera_group(db: AsyncSession, camera_group: CameraGroupSchema):
    new_camera_group = CameraGroup(name=camera_group.name,
                                   address=camera_group.address,
                                   description=camera_group.description)
    db.add(new_camera_group)
    await db.commit()
    await db.refresh(new_camera_group)
    logger.info(f"New camera group created: {new_camera_group.to_dict()}")
    return new_camera_group


async def get_camera_group_by_name(db: AsyncSession, camera_group_name: str):
    camera_group = await db.execute(select(CameraGroup).filter(CameraGroup.name == camera_group_name))
    camera_group = camera_group.scalar_one_or_none()
    if not camera_group:
        logger.info(f"No camera group found with name: {camera_group_name}")
        return None
    logger.info(f"Camera group found: {camera_group.to_dict()}")
    return camera_group


async def get_camera_group_by_id(db: AsyncSession, camera_group_id: int):
    camera_group = await db.execute(select(CameraGroup).filter(CameraGroup.id == camera_group_id))
    camera_group = camera_group.scalar_one_or_none()
    if not camera_group:
        logger.info(f"No camera group found with id: {camera_group_id}")
        return None
    logger.info(f"Camera group found: {camera_group.to_dict()}")
    return camera_group


async def search_groups(
        db: AsyncSession,
        filters: dict,
        sort_by: list[str] = None,
        sort_order: list[str] = None,
        page: int = 1,
        count: int = 10
):
    stmt = select(CameraGroup)

    field_column_map = {
        "name": CameraGroup.name,
        "description": CameraGroup.description,
        "address": CameraGroup.address,
        "id": CameraGroup.id,
        "created_at": CameraGroup.created_at,
        "updated_at": CameraGroup.updated_at,
    }

    # Фильтрация
    conditions = []
    for field, value in filters.items():
        if value is None:
            continue

        if field == "created_from" and value is not None:
            conditions.append(CameraGroup.created_at >= value)
        elif field == "created_to" and value is not None:
            conditions.append(CameraGroup.created_at <= value)
        elif field == "updated_from" and value is not None:
            conditions.append(CameraGroup.updated_at >= value)
        elif field == "updated_to" and value is not None:
            conditions.append(CameraGroup.updated_at <= value)
        elif field == "id":
            conditions.append(cast(CameraGroup.id, String).ilike(f"%{value}%"))
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

    result = await db.execute(stmt.offset((page - 1) * count).limit(count))
    return result.scalars().all()


async def delete_group(db: AsyncSession, camera_group: CameraGroup):
    result = await db.execute(select(CameraGroup).filter(CameraGroup.id == camera_group.id))
    db_group = result.scalar_one_or_none()
    if not db_group:
        logger.warning(f"Camera group {camera_group.id} not found.")
        return None
    logger.info(f"Deleted camera group {db_group.to_dict()}")
    await db.delete(db_group)
    await db.commit()
    return db_group


async def update_group(db: AsyncSession, group_id: int, camera_group: CameraGroupSchema):
    try:
        # Получаем пользователя с joined user_data
        result = await db.execute(
            select(CameraGroup)
            .filter(CameraGroup.id == group_id)
        )
        db_group = result.scalar_one_or_none()

        if not db_group:
            logger.error(f"Camera group {group_id} not found")
            return None
        logger.info(f"Camera group found {db_group.to_dict()}")
        update_data = camera_group.model_dump()
        logger.info(f"Camera group update data {update_data}")
        for key, value in update_data.items():
            if hasattr(db_group, key):
                setattr(db_group, key, value)
        db_group.updated_at = datetime.now()
        logger.info(f"Camera group updated {db_group.to_dict()}")
        await db.commit()
        await db.refresh(db_group)
        return db_group

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating camera group {group_id}: {str(e)}", exc_info=True)
        raise


async def count_groups_with_name(db: AsyncSession, name: str):
    db_groups = await db.execute(select(func.count()).select_from(CameraGroup).filter(CameraGroup.name == name))
    count = db_groups.scalar_one()
    logger.info(f"Found {count} camera groups with name {name}")
    return count


async def count_cameras_with_name(db: AsyncSession, name: str):
    db_cameras = await db.execute(select(func.count()).select_from(Camera).filter(Camera.name == name))
    count = db_cameras.scalar_one()
    logger.info(f"Found {count} cameras with name {name}")
    return count


async def count_cameras_with_link(db: AsyncSession, camera_link: str):
    db_cameras = await db.execute(select(func.count()).select_from(Camera).filter(Camera.address_link == camera_link))
    count = db_cameras.scalar_one()
    logger.info(f"Found {count} cameras with link {camera_link}")
    return count


async def create_camera(db: AsyncSession, camera: CameraSchema, camera_group: CameraGroup):
    new_camera = Camera(
        name=camera.name,
        address_link=camera.address_link,
        group_id=camera_group.id,
    )
    logger.info(f"Creating new camera {new_camera.to_dict()}")
    db.add(new_camera)
    await db.commit()
    await db.refresh(new_camera)
    logger.info(f"Created new camera {new_camera.to_dict()}")
    return new_camera


async def get_camera_by_id(db: AsyncSession, camera_id: int):
    db_camera = await db.execute(select(Camera).filter(Camera.id == camera_id))
    db_camera = db_camera.scalar_one_or_none()
    if not db_camera:
        logger.error(f"Camera with id {camera_id} not found")
        return None
    logger.info(f"Found camera with id {db_camera.to_dict()}")
    return db_camera


async def delete_camera_by_id(db: AsyncSession, camera_id: int):
    db_camera = await db.execute(select(Camera).filter(Camera.id == camera_id))
    db_camera = db_camera.scalar_one_or_none()
    if not db_camera:
        logger.error(f"Camera with id {camera_id} not found")
        return None
    logger.info(f"Found camera with id {db_camera.to_dict()}")
    await db.delete(db_camera)
    await db.commit()
    logger.info(f"Deleted camera with id {db_camera.to_dict()}")
    return db_camera


async def search_cameras(
        db: AsyncSession,
        filters: dict,
        sort_by: list[str] = None,
        sort_order: list[str] = None,
        page: int = 1,
        count: int = 10
):
    stmt = select(Camera)
    field_column_map = {
        "id": Camera.id,
        "name": Camera.name,
        "address_link": Camera.address_link,
        "group_id": Camera.group_id,
        "created_at": Camera.created_at,
        "updated_at": Camera.updated_at,
    }

    # Фильтрация
    conditions = []
    for field, value in filters.items():
        if value is None:
            continue

        if field == "created_from" and value is not None:
            conditions.append(Camera.created_at >= value)
        elif field == "created_to" and value is not None:
            conditions.append(Camera.created_at <= value)
        elif field == "updated_from" and value is not None:
            conditions.append(Camera.updated_at >= value)
        elif field == "updated_to" and value is not None:
            conditions.append(Camera.updated_at <= value)
        elif field == "id":
            conditions.append(cast(Camera.id, String).ilike(f"%{value}%"))
        elif field == "group_id":
            column = field_column_map[field]
            conditions.append(column == value)
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

    result = await db.execute(stmt.offset((page - 1) * count).limit(count))
    return result.scalars().all()


async def update_camera(db: AsyncSession, camera_id: int, camera: CameraSchema):
    try:
        # Получаем пользователя с joined user_data
        result = await db.execute(
            select(Camera)
            .filter(Camera.id == camera_id)
        )
        db_camera = result.scalar_one_or_none()

        if not db_camera:
            logger.error(f"Camera {camera_id} not found")
            return None
        logger.info(f"Camera found {db_camera.to_dict()}")
        update_data = camera.model_dump()
        logger.info(f"Camera update data {update_data}")
        for key, value in update_data.items():
            if hasattr(db_camera, key):
                setattr(db_camera, key, value)
        db_camera.updated_at = datetime.now()
        logger.info(f"Camera updated {db_camera.to_dict()}")
        await db.commit()
        await db.refresh(db_camera)
        return db_camera

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating camera {camera_id}: {str(e)}", exc_info=True)
        raise


async def create_user_camera(db: AsyncSession, camera_id: int, user_id: int):
    try:
        camera_user = CameraUserAssociation(camera_id=camera_id, user_id=user_id)
        logger.info(f"New camera sub: {camera_user.to_dict()}")
        db.add(camera_user)
        await db.commit()
        await db.refresh(camera_user)
        return camera_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating camera {camera_id}: {str(e)}", exc_info=True)
        raise


async def delete_user_camera(db: AsyncSession, record_id: int):
    try:
        camera_user = await db.execute(select(CameraUserAssociation).filter(CameraUserAssociation.id == record_id))
        camera_user = camera_user.scalar_one_or_none()
        if not camera_user:
            logger.error(f"Camera {record_id} not found")
            return None
        await db.delete(camera_user)
        await db.commit()
        logger.info(f"Camera {record_id} deleted")
        return camera_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting camera {record_id}: {str(e)}", exc_info=True)
        raise


async def get_camera_subscription_record(db: AsyncSession, record_id: int):
    try:
        camera_subscription = await db.execute(
            select(CameraUserAssociation).filter(CameraUserAssociation.id == record_id))
        camera_subscription = camera_subscription.scalar_one_or_none()
        if not camera_subscription:
            logger.error(f"Camera {record_id} not found")
            return None
        return camera_subscription
    except Exception as e:
        await db.rollback()
        logger.error(f"Error getting camera subscription {record_id}: {str(e)}", exc_info=True)
        raise


async def get_camera_subscription_record_by_user_camera(db: AsyncSession, user_id: int, camera_id: int):
    try:
        camera_subscription = await db.execute(select(CameraUserAssociation).filter(
            and_(
                CameraUserAssociation.user_id == user_id,
                CameraUserAssociation.camera_id == camera_id
            )))
        camera_subscription = camera_subscription.scalar_one_or_none()
        if not camera_subscription:
            logger.error(f"Camera {camera_id} not found")
            return None
        return camera_subscription
    except Exception as e:
        await db.rollback()
        logger.error(f"Error getting camera subscription {camera_id}|{user_id}: {str(e)}", exc_info=True)
        raise


async def delete_camera_subscription_by_id(db: AsyncSession, record_id: int):
    try:
        camera_subscription = await db.execute(
            select(CameraUserAssociation).filter(CameraUserAssociation.id == record_id))
        camera_subscription = camera_subscription.scalar_one_or_none()
        if not camera_subscription:
            logger.error(f"Camera {record_id} not found")
            return None
        await db.delete(camera_subscription)
        await db.commit()
        logger.info(f"Camera {record_id} deleted")
        return camera_subscription
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting camera subscription {record_id}: {str(e)}", exc_info=True)
        raise


async def search_camera_subscriptions(
        db: AsyncSession,
        camera: Camera,
        filters: dict,
        sort_by: list[str] = None,
        sort_order: list[str] = None,
        page: int = 1,
        count: int = 10
):
    # Базовый запрос с оптимизированной загрузкой
    stmt = (
        select(CameraUserAssociation)
        .options(
            joinedload(CameraUserAssociation.camera).load_only(Camera.name, Camera.version),
            joinedload(CameraUserAssociation.user).load_only(User.username)
        )
        .where(CameraUserAssociation.camera_id == camera.id)
    )

    # Маппинг полей для фильтрации
    filter_field_map = {
        "id": CameraUserAssociation.id,
        "user_id": CameraUserAssociation.user_id,
        "user_name": User.username,
        "created_at": CameraUserAssociation.created_at,
        "updated_at": CameraUserAssociation.updated_at,
    }

    # Применение фильтров
    conditions = []
    for field, value in filters.items():
        if value is None or field not in filter_field_map:
            continue

        column = filter_field_map[field]
        if field == "user_name":
            conditions.append(User.username.ilike(f"%{value}%"))
        elif field.endswith("_from"):
            conditions.append(column >= value)
        elif field.endswith("_to"):
            conditions.append(column <= value)
        else:
            conditions.append(column == value)

    if conditions:
        stmt = stmt.join(User).where(and_(*conditions))

    # Применение сортировки
    if sort_by:
        order_clauses = []
        for i, field in enumerate(sort_by):
            if field in filter_field_map:
                order = sort_order[i] if i < len(sort_order) else "asc"
                order_clauses.append(
                    desc(filter_field_map[field]) if order.lower() == "desc"
                    else asc(filter_field_map[field]))

        if order_clauses:
            stmt = stmt.order_by(*order_clauses)

    # Пагинация
    total = await db.scalar(
        select(func.count())
        .select_from(stmt.subquery())
    )

    result = await db.execute(
        stmt.offset((page - 1) * count).limit(count)
    )

    # Формирование результата
    items = []
    for association in result.unique().scalars().all():
        items.append(CameraUserAssociationAdminDTO(
            id=association.id,
            camera_id=association.camera_id,
            camera_name=association.camera.name,
            user_id=association.user_id,
            user_name=association.user.username,
            created_at=association.created_at.isoformat() if association.created_at else None,
            updated_at=association.updated_at.isoformat() if association.updated_at else None,
        ))

    return items


async def get_user_subscriptions(db: AsyncSession, user_id: int):
    result = await db.execute(select(CameraUserAssociation)
                              .options(
        joinedload(CameraUserAssociation.camera).load_only(Camera.name, Camera.version),
        joinedload(CameraUserAssociation.user).load_only(User.username)
    )
                              .where(CameraUserAssociation.user_id == user_id))
    # Формирование результата
    items = []
    for association in result.unique().scalars().all():
        items.append(CameraUserAssociationAdminDTO(
            id=association.id,
            camera_id=association.camera_id,
            camera_name=association.camera.name,
            user_id=association.user_id,
            user_name=association.user.username,
            created_at=association.created_at.isoformat() if association.created_at else None,
            updated_at=association.updated_at.isoformat() if association.updated_at else None,
        ))

    return items
