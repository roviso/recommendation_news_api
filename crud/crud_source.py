from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
# from schemas import article_schema
from models.source_model import Source
from datetime import datetime



class SourceCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        

    async def create_source(self, source: Source):
        self.db_session.add(source)
        await self.db_session.flush()



    async def get_all_source(self) -> List[Source]:
        print("__________ALOMOST THERE___________")
        query = select(Source)
        results = await self.db_session.execute(query)
        print("_____________RTESULT FOUND______________-")
        return results.scalars().all()


    async def get_source_by_name(self, source_name) ->Source:
        query = select(Source).where(Source.name == source_name)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result


    # async def get_source_by_name(self):


# async def add_source(db: Session, source: Source):
#     new_source = source_model.Source(
#         id = source.pk,
#         created_at = datetime.now(),
#         updated_at = datetime.now(),
#         name = source.name,
#         image = source.image,

#         domain = source.domain,
#         link = source.link,

#         link_prefix = source.link_prefix,

#         link_type = source.link_type,

#         selector = source.selector,

#         exception_selector = source.exception_selector,

#         priority = source.priority,

#         image_selector = source.image_selector,

#         default_image = source.default_image,

#         disable = source.disable,

#         analytics_id = source.analytics_id
#     )
#     db.add(new_source)
#     db.commit()
#     db.refresh(new_source)
#     return new_source



# def get_all_source(db: Session):
#     return db.query(source_model.Source).all()