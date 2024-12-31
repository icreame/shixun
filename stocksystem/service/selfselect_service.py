from model.selfselect import SelfSelect,db

class SelfSelectService:

    @staticmethod
    def add_self_select(userid, stockid):
        # 检查是否已经存在
        existing_selfselect = SelfSelect.query.filter_by(userid=userid, stockid=stockid).first()
        if existing_selfselect:
            return {"success": False, "message": "该股票已在您的自选股中"}

        new_selfselect = SelfSelect(userid=userid, stockid=stockid)
        db.session.add(new_selfselect)
        db.session.commit()

        return {"success": True, "message": "股票已添加到自选股"}

    @staticmethod
    def get_user_self_selects(userid):
        selfselects = SelfSelect.query.filter_by(userid=userid).all()
        return [selfselect.stockid for selfselect in selfselects]  # 返回股票id的列表

    @staticmethod
    def remove_self_select(userid, stockid):
        selfselect = SelfSelect.query.filter_by(userid=userid, stockid=stockid).first()
        if not selfselect:
            return {"success": False, "message": "该股票不在您的自选股中"}

        db.session.delete(selfselect)
        db.session.commit()

        return {"success": True, "message": "股票已从自选股中移除"}
