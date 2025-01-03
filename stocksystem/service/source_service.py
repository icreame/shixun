from model.source import Source,db
from sqlalchemy.exc import SQLAlchemyError

class SourceService:

    @staticmethod
    def add_source(sourcename, description=None):
        try:
            new_source = Source(sourcename=sourcename, description=description)
            db.session.add(new_source)
            db.session.commit()
            return {"success": True, "message": "数据来源添加成功", "industryid": new_source.industryid}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_sources():
        try:
            return Source.query.all()
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_source_by_id(sourceid):
        try:
            return Source.query.get(sourceid)
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def update_source(sourceid, sourcename=None, description=None):
        try:
            source = Source.query.get(sourceid)
            if source:
                if sourcename:
                    source.sourcename = sourcename
                if description:
                    source.description = description
                db.session.commit()
                return {"success": True, "message": "数据来源更新成功"}
            else:
                return {"success": False, "message": "数据来源不存在"}
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_source(sourceid):
        try:
            source = Source.query.get(sourceid)
            if source:
                db.session.delete(source)
                db.session.commit()
                return {"success": True, "message": "数据来源已删除"}
            else:
                return {"success": False, "message": "数据来源不存在"}
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}
