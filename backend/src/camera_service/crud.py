from sqlalchemy import select, desc, asc, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.camera_service.schemas import CameraGroupSchema
from src.shared.logger_setup import setup_logger
from src.shared.models import CameraGroup

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
