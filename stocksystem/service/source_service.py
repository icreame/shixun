from model.source import Source,db

class SourceService:

    @staticmethod
    def add_source(sourcename, description=None):
        new_source = Source(sourcename=sourcename, description=description)
        db.session.add(new_source)
        db.session.commit()
        return {"id": new_source.sourceid, "name": new_source.sourcename, "description": new_source.description}

    @staticmethod
    def get_all_sources():
        return Source.query.all()

    @staticmethod
    def get_source_by_id(sourceid):
        return Source.query.get(sourceid)

    @staticmethod
    def update_source(sourceid, sourcename=None, description=None):
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

    @staticmethod
    def delete_source(sourceid):
        source = Source.query.get(sourceid)
        if source:
            db.session.delete(source)
            db.session.commit()
            return {"success": True, "message": "数据来源已删除"}
        else:
            return {"success": False, "message": "数据来源不存在"}
