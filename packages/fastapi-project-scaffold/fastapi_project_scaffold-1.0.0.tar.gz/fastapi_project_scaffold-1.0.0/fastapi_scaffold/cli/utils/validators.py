"""Validators"""


def parse_fields(fields_str: str) -> list:
    """
    解析字段定义字符串
    
    格式: "name:str,age:int,email:str"
    
    Returns:
        [
            {'name': 'name', 'type': 'str', 'required': True},
            {'name': 'age', 'type': 'int', 'required': True},
            ...
        ]
    """
    if not fields_str:
        return []
    
    fields = []
    for field_def in fields_str.split(','):
        field_def = field_def.strip()
        if ':' not in field_def:
            raise ValueError(f"Invalid field definition: {field_def}")
        
        name, type_str = field_def.split(':', 1)
        name = name.strip()
        type_str = type_str.strip()
        
        # 检查是否可选（type?）
        required = True
        if type_str.endswith('?'):
            required = False
            type_str = type_str[:-1]
        
        fields.append({
            'name': name,
            'type': type_str,
            'required': required
        })
    
    return fields


def get_sqlalchemy_type(python_type: str) -> str:
    """
    Python 类型 → SQLAlchemy 类型
    
    Args:
        python_type: Python 类型名称
    
    Returns:
        SQLAlchemy 类型字符串
    """
    TYPE_MAPPING = {
        'str': 'String(255)',
        'text': 'Text',
        'int': 'Integer',
        'float': 'Float',
        'bool': 'Boolean',
        'date': 'Date',
        'datetime': 'DateTime',
        'json': 'JSON',
        'email': 'String(100)',
        'url': 'String(500)',
        'phone': 'String(20)',
    }
    
    return TYPE_MAPPING.get(python_type, 'String(255)')


def get_python_type_hint(python_type: str, required: bool = True) -> str:
    """
    获取 Python 类型提示
    
    Args:
        python_type: Python 类型名称
        required: 是否必需
    
    Returns:
        类型提示字符串
    """
    TYPE_HINTS = {
        'str': 'str',
        'text': 'str',
        'int': 'int',
        'float': 'float',
        'bool': 'bool',
        'date': 'date',
        'datetime': 'datetime',
        'json': 'dict',
        'email': 'str',
        'url': 'str',
        'phone': 'str',
    }
    
    hint = TYPE_HINTS.get(python_type, 'str')
    
    if not required:
        hint = f'Optional[{hint}]'
    
    return hint


def get_pydantic_field(python_type: str, required: bool = True) -> str:
    """
    获取 Pydantic Field 定义
    
    Args:
        python_type: Python 类型名称
        required: 是否必需
    
    Returns:
        Field 定义字符串
    """
    FIELD_CONFIGS = {
        'str': '..., min_length=1, max_length=255',
        'text': '..., min_length=1',
        'int': '..., ge=0',
        'float': '..., ge=0.0',
        'bool': '...',
        'date': '...',
        'datetime': '...',
        'json': '...',
        'email': '..., max_length=100',
        'url': '..., max_length=500',
        'phone': '..., pattern=r"^1[3-9]\\d{9}$"',
    }
    
    config = FIELD_CONFIGS.get(python_type, '...')
    
    if not required:
        config = config.replace('...', 'None')
    
    return f'Field({config})'
