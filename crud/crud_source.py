from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
# from schemas import article_schema
from models.source_model import Source
from models import author_model, article_model
from datetime import datetime
from typing import List, Optional
from sqlalchemy import update,delete


class SourceCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        

    async def create_source(self, source: Source):
        self.db_session.add(source)
        await self.db_session.flush()



    async def get_all_source(self) -> List[Source]:
        query = select(Source)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def get_source_by_id(self, source_id: int) ->Source:
        query = select(Source).where(Source.id == source_id)
        results = await self.db_session.execute(query)
        result = results.first()
        return result


    async def get_source_by_name(self, source_name) ->Source:
        query = select(Source).where(Source.name == source_name)
        results = await self.db_session.execute(query)
        (result,) = results.fetchone()
        return result

    async def get_source_authors(self, source_id: int) ->List[author_model.Author]:
        query = select(author_model.Author).filter(author_model.Author.source_id == source_id)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    async def get_source_articles(self, source_id: int) ->List[article_model.Article]:
        query = select(article_model.Article).filter(article_model.Article.source_id == source_id).order_by(article_model.Article.date.desc())
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    async def update_source(self, source_id: int,
                            name: Optional[str], 
                            link: Optional[str], 
                            image: Optional[str],
                            content_selector: Optional[str],
                            image_selector: Optional[str],
                            author_img_selector: Optional[str],
                            author_name_selector: Optional[str],
                            label_selector: Optional[str],
                            disable: Optional[str],
                            analytics_id: Optional[str],
                            debug: Optional[str],
                            debug_link: Optional[str]
                            ):
        
        """ Update the source info"""
        q = update(Source).where(Source.id == source_id)
        if name:
            q = q.values(name=name)
        if link:
            q = q.values(link=link)
        if image:
            q = q.values(image=image)
        if content_selector:
            q = q.values(content_selector=content_selector)
        if image_selector:
            q = q.values(image_selector=image_selector)
        if author_img_selector:
            q = q.values(author_img_selector=author_img_selector)
        if author_name_selector:
            q = q.values(author_name_selector=author_name_selector)
        if label_selector:
            q = q.values(label_selector=label_selector)
        if disable:
            q = q.values(disable=disable)
        if analytics_id:
            q = q.values(analytics_id=analytics_id)
        if debug:
            q = q.values(debug=debug)
        if debug_link:
            q = q.values(debug_link=debug_link)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    async def remove_source(self, source_id: int):
        query = delete(Source).where(Source.id == source_id)
        await self.db_session.execute(query)


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