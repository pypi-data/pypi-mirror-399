"""Code Generation Utilities"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from cli.utils.validators import (
    parse_fields,
    get_sqlalchemy_type,
    get_python_type_hint,
    get_pydantic_field
)


def render_template(template_name: str, context: dict) -> str:
    """
    渲染 Jinja2 模板
    
    Args:
        template_name: 模板文件名
        context: 模板上下文
    
    Returns:
        渲染后的内容
    """
    templates_dir = Path(__file__).parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template(template_name)
    return template.render(**context)


def generate_model(module_name: str, class_name: str, fields: list) -> str:
    """
    生成 Model 代码
    
    Args:
        module_name: 模块名（如 article）
        class_name: 类名（如 Article）
        fields: 字段列表
    
    Returns:
        生成的代码
    """
    # 转换字段为模板所需格式
    template_fields = []
    has_date = False
    
    for field in fields:
        field_type = field['type']
        required = field['required']
        
        # SQLAlchemy 类型
        sa_type = get_sqlalchemy_type(field_type)
        
        # Python 类型提示
        base_type = get_python_type_hint(field_type, required=True)
        type_hint = get_python_type_hint(field_type, required=required)
        
        # 检查是否需要导入 date
        if field_type in ['date', 'datetime']:
            has_date = True
        
        template_fields.append({
            'name': field['name'],
            'type': field_type,
            'required': required,
            'sa_type': sa_type,
            'type_hint': type_hint,
            'base_type': base_type,
        })
    
    context = {
        'module_name': module_name,
        'class_name': class_name,
        'table_name': f"{module_name}s",  # 简单复数形式
        'fields': template_fields,
        'has_date': has_date
    }
    
    return render_template('model.py.j2', context)


def generate_schema(module_name: str, class_name: str, fields: list) -> str:
    """生成 Schema 代码"""
    template_fields = []
    has_date = False
    
    for field in fields:
        field_type = field['type']
        required = field['required']
        
        # Python 类型提示
        base_type = get_python_type_hint(field_type, required=True)
        type_hint = get_python_type_hint(field_type, required=required)
        
        # Pydantic Field
        pydantic_field = get_pydantic_field(field_type, required=required)
        
        # 检查是否需要导入 date
        if field_type in ['date', 'datetime']:
            has_date = True
        
        template_fields.append({
            'name': field['name'],
            'type': field_type,
            'required': required,
            'type_hint': type_hint,
            'base_type': base_type,
            'pydantic_field': pydantic_field,
        })
    
    context = {
        'module_name': module_name,
        'class_name': class_name,
        'fields': template_fields,
        'has_date': has_date
    }
    
    return render_template('schema.py.j2', context)


def generate_crud(module_name: str, class_name: str) -> str:
    """生成 CRUD 代码"""
    context = {
        'module_name': module_name,
        'class_name': class_name,
    }
    
    return render_template('crud.py.j2', context)


def generate_api(
    module_name: str,
    class_name: str,
    api_prefix: str = None,
    api_tag: str = None,
    auth: bool = True
) -> str:
    """生成 API 代码"""
    if api_prefix is None:
        api_prefix = f"/api/v1/{module_name}s"
    
    if api_tag is None:
        api_tag = f"{class_name}管理"
    
    context = {
        'module_name': module_name,
        'class_name': class_name,
        'api_prefix': api_prefix,
        'api_tag': api_tag,
        'auth': auth,
    }
    
    return render_template('api.py.j2', context)


def to_class_name(module_name: str) -> str:
    """
    模块名转类名
    
    Examples:
        article -> Article
        blog_post -> BlogPost
    """
    return ''.join(word.capitalize() for word in module_name.split('_'))


def to_table_name(module_name: str) -> str:
    """
    模块名转表名（简单复数）
    
    Examples:
        article -> articles
        blog_post -> blog_posts
    """
    return f"{module_name}s"
