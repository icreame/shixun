from flask import Blueprint, request, jsonify
from service.source_service import SourceService

source_blueprint = Blueprint('source', __name__)

# 添加数据来源
@source_blueprint.route('/add', methods=['POST'])
def add_source():
    data = request.json
    sourcename = data.get('sourcename')
    description = data.get('description')

    if not sourcename:
        return jsonify({"success": False, "message": "数据来源名称不能为空"}), 400

    result = SourceService.add_source(sourcename, description)
    return jsonify({"success": True, "message": "数据来源已添加", "source": result})

# 获取所有数据来源
@source_blueprint.route('/all', methods=['GET'])
def get_all_sources():
    sources = SourceService.get_all_sources()
    return jsonify({"success": True, "sources": [source.sourcename for source in sources]})

# 根据 sourceid 获取数据来源
@source_blueprint.route('/<int:sourceid>', methods=['GET'])
def get_source_by_id(sourceid):
    source = SourceService.get_source_by_id(sourceid)
    if source:
        return jsonify({"success": True, "source": {"id": source.sourceid, "name": source.sourcename, "description": source.description}})
    else:
        return jsonify({"success": False, "message": "数据来源不存在"}), 404

# 更新数据来源
@source_blueprint.route('/update', methods=['POST'])
def update_source():
    data = request.json
    sourceid = data.get('sourceid')
    sourcename = data.get('sourcename')
    description = data.get('description')

    if not sourceid:
        return jsonify({"success": False, "message": "sourceid不能为空"}), 400

    result = SourceService.update_source(sourceid, sourcename, description)
    return jsonify(result)

# 删除数据来源, 建议不要用这个接口, 有外键依赖
@source_blueprint.route('/<int:sourceid>', methods=['DELETE'])
def delete_source(sourceid):
    result = SourceService.delete_source(sourceid)
    return jsonify(result)
