from model.industry import db, Industry
from sqlalchemy.exc import SQLAlchemyError


class IndustryService:
    @staticmethod
    def create_industry(industryname, description=None):
        try:
            new_industry = Industry(industryname=industryname, description=description)
            db.session.add(new_industry)
            db.session.commit()
            return {"success": True, "message": "行业创建成功", "industryid": new_industry.industryid}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_industry_by_id(industryid):
        try:
            industry = Industry.query.get(industryid)
            if industry:
                return {"success": True, "industry": {
                    "industryid": industry.industryid,
                    "industryname": industry.industryname,
                    "description": industry.description
                }}
            else:
                return {"success": False, "message": "行业不存在"}
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_industries():
        try:
            industries = Industry.query.all()
            industries_list = [
                {"industryid": i.industryid, "industryname": i.industryname, "description": i.description} for i in
                industries]
            return {"success": True, "industries": industries_list}
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def update_industry(industryid, new_name=None, new_description=None):
        try:
            industry = Industry.query.get(industryid)
            if not industry:
                return {"success": False, "message": "行业不存在"}

            if new_name:
                industry.industryname = new_name
            if new_description:
                industry.description = new_description

            db.session.commit()
            return {"success": True, "message": "行业更新成功"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_industry(industryid):
        try:
            industry = Industry.query.get(industryid)
            if not industry:
                return {"success": False, "message": "行业不存在"}

            db.session.delete(industry)
            db.session.commit()
            return {"success": True, "message": "行业删除成功"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
