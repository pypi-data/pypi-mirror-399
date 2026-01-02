"""
Deep Code Analysis Module for App Memory System

Extracts meaningful code intelligence from Python files including:
- Functions/methods with signatures and docstrings
- Classes and their attributes
- Django models with fields and relationships
- Imports and cross-app dependencies
- URL patterns
- Variables and constants
"""

import ast
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes Python source code to extract structural information"""

    def __init__(self, file_path: Path, app_root: Path):
        self.file_path = file_path
        self.app_root = app_root
        self.relative_path = str(file_path.relative_to(app_root))
        self.source_code = None
        self.tree = None

    def analyze(self) -> Dict[str, Any]:
        """Perform complete analysis of the file"""
        try:
            self.source_code = self.file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {self.relative_path}, trying latin-1")
            try:
                self.source_code = self.file_path.read_text(encoding='latin-1')
            except Exception as e:
                logger.error(f"Failed to read {self.relative_path}: {e}")
                return {
                    "path": self.relative_path,
                    "error": f"Failed to read file: {str(e)}",
                    "type": "unreadable"
                }
        except Exception as e:
            logger.error(f"Error reading {self.relative_path}: {e}")
            return {
                "path": self.relative_path,
                "error": f"Failed to read: {str(e)}",
                "type": "unreadable"
            }

        try:
            self.tree = ast.parse(self.source_code, filename=str(self.file_path))
        except SyntaxError as e:
            logger.debug(f"Syntax error in {self.relative_path}: {e}")
            return {
                "path": self.relative_path,
                "error": f"Syntax error: {str(e)}",
                "type": "unparseable"
            }
        except Exception as e:
            logger.error(f"Failed to parse {self.relative_path}: {e}")
            return {
                "path": self.relative_path,
                "error": f"Failed to parse: {str(e)}",
                "type": "unparseable"
            }

        file_type = self._detect_file_type()

        analysis = {
            "path": self.relative_path,
            "type": file_type,
            "size": self.file_path.stat().st_size,
        }

        # Extract basic structural information with error handling
        try:
            analysis["imports"] = self._extract_imports()
        except Exception as e:
            logger.warning(f"Error extracting imports from {self.relative_path}: {e}")
            analysis["imports"] = {"standard_library": [], "third_party": [], "django": [], "local_apps": [], "relative": []}

        try:
            analysis["classes"] = self._extract_classes()
        except Exception as e:
            logger.warning(f"Error extracting classes from {self.relative_path}: {e}")
            analysis["classes"] = []

        try:
            analysis["functions"] = self._extract_functions()
        except Exception as e:
            logger.warning(f"Error extracting functions from {self.relative_path}: {e}")
            analysis["functions"] = []

        try:
            analysis["constants"] = self._extract_constants()
        except Exception as e:
            logger.warning(f"Error extracting constants from {self.relative_path}: {e}")
            analysis["constants"] = []

        # Add specialized analysis based on file type
        try:
            if file_type == "models":
                analysis["models"] = self._extract_django_models()
            elif file_type == "views":
                analysis["views"] = self._extract_django_views()
            elif file_type == "urls":
                analysis["url_patterns"] = self._extract_url_patterns()
            elif file_type == "forms":
                analysis["forms"] = self._extract_django_forms()
            elif file_type == "admin":
                analysis["admin_classes"] = self._extract_django_admin()
            elif file_type == "serializers":
                analysis["serializers"] = self._extract_drf_serializers()
        except Exception as e:
            logger.warning(f"Error in specialized analysis for {self.relative_path}: {e}")

        return analysis

    def _detect_file_type(self) -> str:
        """Detect the type of Django/Python file"""
        filename = self.file_path.name

        if filename == "models.py":
            return "models"
        elif filename == "views.py":
            return "views"
        elif filename == "urls.py":
            return "urls"
        elif filename == "forms.py":
            return "forms"
        elif filename == "admin.py":
            return "admin"
        elif filename == "serializers.py":
            return "serializers"
        elif filename == "tests.py" or filename.startswith("test_"):
            return "tests"
        elif filename == "apps.py":
            return "config"
        elif filename == "settings.py":
            return "settings"
        elif filename == "tasks.py":
            return "celery_tasks"
        elif filename == "consumers.py":
            return "websocket_consumers"
        else:
            return "module"

    def _extract_imports(self) -> Dict[str, List[str]]:
        """Extract all imports with categorization"""
        imports = {
            "standard_library": [],
            "third_party": [],
            "django": [],
            "local_apps": [],
            "relative": []
        }

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    self._categorize_import(module, imports)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module
                    imported_names = [alias.name for alias in node.names]
                    self._categorize_import(module, imports, imported_names)

        return imports

    def _categorize_import(self, module: str, imports: Dict, names: List[str] = None):
        """Categorize import by type"""
        import_info = f"{module}" + (f" ({', '.join(names)})" if names else "")

        if module.startswith('.'):
            imports["relative"].append(import_info)
        elif module.startswith('django'):
            imports["django"].append(import_info)
        elif module in ['os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 're', 'hashlib']:
            imports["standard_library"].append(import_info)
        elif any(module.startswith(pkg) for pkg in ['celery', 'channels', 'rest_framework', 'paramiko', 'docker']):
            imports["third_party"].append(import_info)
        else:
            # Assume local app
            imports["local_apps"].append(import_info)

    def _extract_classes(self) -> List[Dict[str, Any]]:
        """Extract all class definitions"""
        classes = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "bases": [self._get_name(base) for base in node.bases],
                    "docstring": ast.get_docstring(node),
                    "methods": [],
                    "attributes": []
                }

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = self._extract_function_info(item)
                        class_info["methods"].append(method_info)
                    elif isinstance(item, ast.Assign):
                        # Class-level attributes
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info["attributes"].append(target.id)

                classes.append(class_info)

        return classes

    def _extract_functions(self) -> List[Dict[str, Any]]:
        """Extract top-level functions"""
        functions = []

        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(self._extract_function_info(node))

        return functions

    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed information about a function/method"""
        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = self._get_name(arg.annotation)
            params.append(param_info)

        return_type = None
        if node.returns:
            return_type = self._get_name(node.returns)

        decorators = [self._get_name(dec) for dec in node.decorator_list]

        return {
            "name": node.name,
            "params": params,
            "return_type": return_type,
            "decorators": decorators,
            "docstring": ast.get_docstring(node),
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }

    def _extract_constants(self) -> List[Dict[str, Any]]:
        """Extract module-level constants (UPPERCASE variables)"""
        constants = []

        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        value_repr = self._get_value_repr(node.value)
                        constants.append({
                            "name": target.id,
                            "value": value_repr
                        })

        return constants

    def _extract_django_models(self) -> List[Dict[str, Any]]:
        """Extract Django model definitions"""
        models = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from models.Model
                base_names = [self._get_name(base) for base in node.bases]
                if any('Model' in base for base in base_names):
                    model_info = {
                        "name": node.name,
                        "fields": [],
                        "meta": {},
                        "methods": [],
                        "docstring": ast.get_docstring(node)
                    }

                    for item in node.body:
                        # Extract fields
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    field_type = self._get_field_type(item.value)
                                    if field_type:
                                        model_info["fields"].append({
                                            "name": target.id,
                                            "type": field_type,
                                            "options": self._get_field_options(item.value)
                                        })

                        # Extract Meta class
                        elif isinstance(item, ast.ClassDef) and item.name == "Meta":
                            meta_info = {}
                            for meta_item in item.body:
                                if isinstance(meta_item, ast.Assign):
                                    for target in meta_item.targets:
                                        if isinstance(target, ast.Name):
                                            meta_info[target.id] = self._get_value_repr(meta_item.value)
                            model_info["meta"] = meta_info

                        # Extract methods
                        elif isinstance(item, ast.FunctionDef):
                            model_info["methods"].append(item.name)

                    models.append(model_info)

        return models

    def _extract_django_views(self) -> List[Dict[str, Any]]:
        """Extract Django views (function and class-based)"""
        views = []

        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                # Check if it looks like a view (has request parameter)
                if node.args.args and node.args.args[0].arg == 'request':
                    views.append({
                        "type": "function",
                        "name": node.name,
                        "decorators": [self._get_name(dec) for dec in node.decorator_list],
                        "docstring": ast.get_docstring(node)
                    })
            elif isinstance(node, ast.ClassDef):
                # Check if it's a class-based view
                base_names = [self._get_name(base) for base in node.bases]
                if any('View' in base for base in base_names):
                    views.append({
                        "type": "class",
                        "name": node.name,
                        "bases": base_names,
                        "methods": [item.name for item in node.body if isinstance(item, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node)
                    })

        return views

    def _extract_url_patterns(self) -> List[Dict[str, Any]]:
        """Extract URL patterns from urls.py"""
        patterns = []

        # Look for urlpatterns list
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'urlpatterns':
                        if isinstance(node.value, ast.List):
                            for element in node.value.elts:
                                pattern_info = self._parse_url_pattern(element)
                                if pattern_info:
                                    patterns.append(pattern_info)

        return patterns

    def _parse_url_pattern(self, node) -> Optional[Dict[str, Any]]:
        """Parse a single URL pattern"""
        if isinstance(node, ast.Call):
            func_name = self._get_name(node.func)
            if func_name in ['path', 'url', 're_path', 'include']:
                pattern_info = {"type": func_name}

                if node.args:
                    # First arg is the route
                    if isinstance(node.args[0], ast.Constant):
                        pattern_info["route"] = node.args[0].value

                    # Second arg is the view or include
                    if len(node.args) > 1:
                        pattern_info["view"] = self._get_name(node.args[1])

                # Check for name kwarg
                for keyword in node.keywords:
                    if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                        pattern_info["name"] = keyword.value.value

                return pattern_info

        return None

    def _extract_django_forms(self) -> List[Dict[str, Any]]:
        """Extract Django form definitions"""
        forms = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                base_names = [self._get_name(base) for base in node.bases]
                if any('Form' in base for base in base_names):
                    form_info = {
                        "name": node.name,
                        "type": base_names[0] if base_names else "Form",
                        "fields": [],
                        "meta": {}
                    }

                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    field_type = self._get_field_type(item.value)
                                    if field_type:
                                        form_info["fields"].append({
                                            "name": target.id,
                                            "type": field_type
                                        })
                        elif isinstance(item, ast.ClassDef) and item.name == "Meta":
                            for meta_item in item.body:
                                if isinstance(meta_item, ast.Assign):
                                    for target in meta_item.targets:
                                        if isinstance(target, ast.Name):
                                            form_info["meta"][target.id] = self._get_value_repr(meta_item.value)

                    forms.append(form_info)

        return forms

    def _extract_django_admin(self) -> List[Dict[str, Any]]:
        """Extract Django admin registrations"""
        admin_classes = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                base_names = [self._get_name(base) for base in node.bases]
                if any('Admin' in base for base in base_names):
                    admin_info = {
                        "name": node.name,
                        "model": None,
                        "list_display": [],
                        "list_filter": [],
                        "search_fields": [],
                        "other_options": {}
                    }

                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    attr_name = target.id
                                    value_repr = self._get_value_repr(item.value)

                                    if attr_name == "list_display":
                                        admin_info["list_display"] = value_repr
                                    elif attr_name == "list_filter":
                                        admin_info["list_filter"] = value_repr
                                    elif attr_name == "search_fields":
                                        admin_info["search_fields"] = value_repr
                                    else:
                                        admin_info["other_options"][attr_name] = value_repr

                    admin_classes.append(admin_info)

        return admin_classes

    def _extract_drf_serializers(self) -> List[Dict[str, Any]]:
        """Extract Django REST Framework serializers"""
        serializers = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                base_names = [self._get_name(base) for base in node.bases]
                if any('Serializer' in base for base in base_names):
                    serializer_info = {
                        "name": node.name,
                        "type": base_names[0] if base_names else "Serializer",
                        "fields": [],
                        "meta": {}
                    }

                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    field_type = self._get_field_type(item.value)
                                    if field_type:
                                        serializer_info["fields"].append({
                                            "name": target.id,
                                            "type": field_type
                                        })
                        elif isinstance(item, ast.ClassDef) and item.name == "Meta":
                            for meta_item in item.body:
                                if isinstance(meta_item, ast.Assign):
                                    for target in meta_item.targets:
                                        if isinstance(target, ast.Name):
                                            serializer_info["meta"][target.id] = self._get_value_repr(meta_item.value)

                    serializers.append(serializer_info)

        return serializers

    def _get_field_type(self, node) -> Optional[str]:
        """Extract field type from a field assignment"""
        if isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None

    def _get_field_options(self, node) -> Dict[str, Any]:
        """Extract field options from a field call"""
        options = {}
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                options[keyword.arg] = self._get_value_repr(keyword.value)
        return options

    def _get_name(self, node) -> str:
        """Get the name from various AST node types"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f"{value}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(type(node).__name__)

    def _get_value_repr(self, node) -> Any:
        """Get a representation of a value node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._get_value_repr(elt) for elt in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._get_value_repr(elt) for elt in node.elts)
        elif isinstance(node, ast.Dict):
            return {self._get_value_repr(k): self._get_value_repr(v)
                    for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_name(node)
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else repr(node)


def analyze_file(file_path: Path, app_root: Path) -> Dict[str, Any]:
    """
    Analyze a single file and return structured context

    Args:
        file_path: Path to the file to analyze
        app_root: Root directory of the app

    Returns:
        Dictionary with file analysis
    """
    # Only analyze Python files
    if file_path.suffix != '.py':
        return {
            "path": str(file_path.relative_to(app_root)),
            "type": "non_python",
            "size": file_path.stat().st_size,
            "extension": file_path.suffix
        }

    analyzer = CodeAnalyzer(file_path, app_root)
    return analyzer.analyze()
