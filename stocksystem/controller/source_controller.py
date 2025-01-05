from flask import Blueprint, request, jsonify
from service.source_service import SourceService

source_blueprint = Blueprint('source', __name__)


@source_blueprint.route('/add', methods=['POST'])
def add_source():
    """
    添加数据来源
    """
    data = request.json
    sourcename = data.get('sourcename')
    description = data.get('description')

    if not sourcename:
        return jsonify({"success": False, "message": "数据来源名称不能为空"}), 400

    result = SourceService.add_source(sourcename, description)
    return jsonify({"success": True, "message": "数据来源已添加", "source": result})


@source_blueprint.route('/all', methods=['GET'])
def get_all_sources():
    """
    获取数据来源
    """
    sources = SourceService.get_all_sources()
    return jsonify({"success": True, "sources": sources})


@source_blueprint.route('/<int:sourceid>', methods=['GET'])
def get_source_by_id(sourceid):
    """
    根据id获取数据来源
    """
    source = SourceService.get_source_by_id(sourceid)
    if source:
        return jsonify({"success": True, "source": {"id": source.sourceid, "name": source.sourcename, "description": source.description}})
    else:
        return jsonify({"success": False, "message": "数据来源不存在"}), 404


@source_blueprint.route('/update', methods=['PUT'])
def update_source():
    """
    更新数据来源
    """
    data = request.json
    sourceid = data.get('sourceid')
    sourcename = data.get('sourcename')
    description = data.get('description')

    if not sourceid:
        return jsonify({"success": False, "message": "sourceid不能为空"}), 400

    result = SourceService.update_source(sourceid, sourcename, description)
    return jsonify(result)


@source_blueprint.route('/delete/<int:sourceid>', methods=['DELETE'])
def delete_source(sourceid):
    """
    删除数据来源
    """
    result = SourceService.delete_source(sourceid)
    return jsonify(result)
