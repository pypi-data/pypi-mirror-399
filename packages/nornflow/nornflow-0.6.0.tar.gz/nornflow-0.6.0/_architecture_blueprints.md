# NornFlow Blueprint Feature: Complete Architecture Documentation

## 1. Executive Summary

The Blueprint feature introduces a powerful reusability mechanism to NornFlow, enabling users to define reusable task sequences that can be composed into workflows. Blueprints are designed as "task macros" that expand at workflow load time, supporting nested composition with circular dependency detection while maintaining NornFlow's simple execution model. 

**Dynamic Blueprint Resolution**: Blueprint references and conditional inclusion support Jinja2 templating using assembly-time variables (workflow vars, CLI vars, environment vars, and domain defaults), enabling environment-specific workflow composition while maintaining compile-time expansion.

## 2. Theoretical Foundation

### 2.1 Design Philosophy

Blueprints follow the **Macro Expansion Pattern with Dynamic Resolution**:

```
MACRO EXPANSION (Our Approach):
Workflow Definition → Resolve Blueprint Templates → Conditionally Include → Expand to Tasks → Single Task List → Execute
                      (using assembly-time vars)    (using assembly-time vars)

COMPOSITION (Not Our Approach):
Workflow Definition → Blueprint Reference → Runtime Resolution → Nested Execution
```

**Core Characteristics**: 
- Compile-time expansion during `WorkflowModel.create()`
- Dynamic blueprint reference resolution using assembly-time variables
- Conditional blueprint inclusion using assembly-time variables
- Recursive nested blueprint support with path-based circular detection
- Zero runtime overhead
- Preserves linear task execution model
- Maintains sequential task ID assignment
- Content-based identity for robust circular detection

### 2.2 Core Principles

1. **Compile-Time Resolution**: Blueprints expand during workflow loading, before any execution context exists
2. **Dynamic Template Resolution**: Blueprint references and conditions can use Jinja2 templates with assembly-time variables
3. **Conditional Inclusion**: Blueprints can be conditionally included based on assembly-time variable evaluation
4. **Recursive Composition**: Blueprints can reference other blueprints, enabling modular design
5. **Path-Based Circular Detection**: Detects cycles within expansion paths while allowing repeated sequential use
6. **Content-Based Identity**: Uses content hashing to identify blueprints regardless of file path
7. **Transparency**: Once expanded, blueprint tasks are indistinguishable from regular tasks

### 2.3 Comparison with Ansible

NornFlow is a **specialized network automation tool**, not a general-purpose platform like Ansible. Understanding Ansible's reusability constructs helps position NornFlow blueprints correctly.

#### Ansible's Reusability Constructs

**Roles** are complete, self-contained automation units with a defined directory structure:
```
roles/
└── configure_ospf/
    ├── tasks/main.yml       # Primary task list
    ├── handlers/main.yml    # Event handlers
    ├── vars/main.yml        # Role variables (high precedence)
    ├── defaults/main.yml    # Default variables (lowest precedence)
    ├── files/               # Static files to copy
    ├── templates/           # Jinja2 templates
    ├── meta/main.yml        # Role dependencies and metadata
    └── library/             # Custom modules
```

**Task Files** are simple YAML lists of tasks that can be included:
```yaml
# tasks/common.yml
- name: Install packages
  package:
    name: "{{ item }}"
  loop: "{{ required_packages }}"

# In playbook:
- include_tasks: tasks/common.yml  # Dynamic, evaluated at runtime
- import_tasks: tasks/common.yml   # Static, processed at parse time
```

#### Where Blueprints Fit

| Ansible Construct | NornFlow Equivalent | Comparison |
|-------------------|---------------------|------------|
| Roles | Not applicable | NornFlow maintains simplicity—no handlers, templates, or variable scopes |
| `import_tasks` (static) | **Blueprints** (closest) | Both expand at parse time, but blueprints add dynamic resolution |
| `include_tasks` (dynamic) | Not applicable | Runtime resolution incompatible with compile-time model |
| Playbooks | Workflows | Top-level execution units |

**Blueprints occupy a unique middle ground between Ansible's `import_tasks` and `include_tasks`:**

**Similarities to `import_tasks` (Static Processing)**:
- Both are processed at **parse/compile time**, not runtime
- Both expand into the parent's task list before execution begins
- Both maintain a flat execution model (no nested execution contexts)
- Both preserve sequential task ordering

**Key Differences from `import_tasks`**:
- **Dynamic Resolution**: Blueprint references can use Jinja2 templates
  ```yaml
  # Ansible import_tasks - static path only
  - import_tasks: tasks/common.yml  # ✅ Works
  - import_tasks: "tasks/{{ env }}_tasks.yml"  # ❌ Not supported
  
  # NornFlow blueprints - dynamic references supported
  - blueprint: common  # ✅ Works
  - blueprint: "{{ env }}_validation"  # ✅ Also works!
  ```

- **Conditional Inclusion**: Blueprints support `if` field with Jinja2 expressions
  ```yaml
  # Ansible import_tasks - no conditional support
  - import_tasks: tasks/common.yml
    when: env == "prod"  # ❌ Ignored (when is runtime, import is parse-time)
  
  # NornFlow blueprints - assembly-time conditionals
  - blueprint: prod_checks
    if: "{{ env == 'prod' }}"  # ✅ Evaluated at parse time
  ```

**Distinctions from `include_tasks` (Dynamic Processing)**:
- **Variable Context**: Blueprints use assembly-time variables (ENV, domain, workflow, CLI), not runtime/host variables
- **Timing**: Blueprint expansion happens during workflow loading, not during execution
- **No Runtime Overhead**: Once expanded, blueprints are transparent (versus `include_tasks` which evaluates per-host at runtime)

**Additional NornFlow-Specific Features**:
- **Nested Composition**: Blueprints can reference other blueprints (with circular detection)
- **Content-Based Identity**: Uses content hashing for robust circular detection
- **No Variable Scoping**: Blueprints inherit the complete workflow variable context
- **Path-Based Detection**: Allows legitimate repeated use while preventing circular dependencies

**In Summary**: NornFlow blueprints are most comparable to Ansible's `import_tasks` in their **compile-time expansion philosophy**, but enhance this with **assembly-time dynamic resolution** that `import_tasks` lacks. This provides practical environment-specific workflow composition while maintaining the performance and predictability benefits of static expansion.

This intentional design aligns with NornFlow's philosophy of providing focused, Python-native network automation without the complexity of general-purpose platforms while still enabling flexible, environment-aware deployments.

## 3. Nested Blueprint Architecture

### 3.1 Recursive Expansion Design

Blueprints support arbitrary nesting depth with automatic circular dependency detection:

```
Workflow
  ├── Task A
  ├── Blueprint X (resolved from {{ env }}_checks, conditionally included)
  │     ├── Task B
  │     ├── Blueprint Y (conditionally included)
  │     │     ├── Task C
  │     │     └── Task D
  │     └── Task E
  └── Task F

Expands to: Task A → Task B → Task C → Task D → Task E → Task F
(assuming all conditions evaluate to true)
```

### 3.2 Circular vs Repeated Use

A critical distinction exists between **circular dependencies** (invalid) and **repeated use** (valid):

**Circular Dependency (INVALID)** - Blueprint appears within its own expansion chain:
```
Blueprint A → Blueprint B → Blueprint A → ... (infinite loop)
```

**Repeated Sequential Use (VALID)** - Same blueprint used multiple times at the same nesting level:
```yaml
tasks:
  - blueprint: health_check    # Expands, completes
  - name: configure_device
  - blueprint: health_check    # Valid: previous expansion finished
  - name: save_config
  - blueprint: health_check    # Valid: can repeat as needed
```

### 3.3 Path-Based Circular Detection Algorithm

The algorithm uses a **stack** that tracks only the current nested expansion path. When a blueprint finishes expanding, it's popped from the stack, allowing legitimate reuse:

```python
@classmethod
def _expand_blueprint_references(
    cls, 
    task_list: list[dict[str, Any]],
    var_context: dict[str, Any],
    expansion_stack: list[str] | None = None,
    content_cache: dict[str, list[dict[str, Any]]] | None = None
) -> list[dict[str, Any]]:
    """
    Expand blueprint references with path-based circular detection and conditional inclusion.
    
    Uses content hashing for blueprint identity to handle cases where the same
    blueprint is referenced via different paths (catalog name, relative path,
    absolute path) or identical content exists in multiple locations.
    
    Args:
        task_list: List of task/blueprint definitions to expand.
        var_context: Variable context for template resolution (assembly-time vars only).
        expansion_stack: Current expansion path for circular detection (content hashes).
        content_cache: Cache mapping content hash to parsed tasks.
        
    Returns:
        Fully expanded list of task dictionaries.
        
    Raises:
        BlueprintCircularDependencyError: If circular dependency detected.
        BlueprintError: If blueprint not found or has invalid structure.
        WorkflowError: If template resolution fails.
    """
    if not expansion_stack:
        expansion_stack = []
    if not content_cache:
        content_cache = {}
    
    expanded = []
    
    for item in task_list:
        if "blueprint" in item and "name" not in item:
            # NEW: Evaluate 'if' condition first (if present)
            if "if" in item:
                condition_result = cls._evaluate_blueprint_condition(item["if"], var_context)
                if not condition_result:
                    logger.debug(
                        f"Skipping blueprint '{item['blueprint']}' due to false 'if' condition"
                    )
                    continue
            
            blueprint_ref = item["blueprint"]
            
            # Resolve Jinja2 template in blueprint reference
            resolved_ref = cls._resolve_blueprint_template(blueprint_ref, var_context)
            
            # Resolve to file path, then get content-based identity
            blueprint_path = cls._resolve_blueprint_to_path(resolved_ref)
            content_hash = _get_file_content_hash(blueprint_path)
            
            # Circular check using content hash
            if content_hash in expansion_stack:
                raise BlueprintCircularDependencyError(
                    resolved_ref,
                    expansion_stack.copy()
                )
            
            # Push before expanding
            expansion_stack.append(content_hash)
            
            try:
                # Load tasks with caching
                if content_hash not in content_cache:
                    content_cache[content_hash] = cls._load_blueprint_tasks(blueprint_path)
                
                blueprint_tasks = content_cache[content_hash]
                expanded_blueprint = cls._expand_blueprint_references(
                    blueprint_tasks,
                    var_context,
                    expansion_stack,
                    content_cache
                )
                expanded.extend(expanded_blueprint)
            finally:
                # Pop after expanding - allows reuse at same level
                expansion_stack.pop()
        
        elif "name" in item and "blueprint" not in item:
            expanded.append(item)
        else:
            raise BlueprintError(
                f"Invalid task definition: must have 'name' XOR 'blueprint'. Keys: {list(item.keys())}"
            )
    
    return expanded
```

### 3.4 Dependency Scenarios

**Valid: Repeated Sequential Use**
```yaml
tasks:
  - blueprint: health_check    # Stack: [hash_hc] → expansion → Stack: []
  - name: configure_device
  - blueprint: health_check    # Stack: [hash_hc] → expansion → Stack: [] (VALID)
  - name: save_config
```

**Valid: Different Branches**
```yaml
# blueprints/deploy.yaml
tasks:
  - blueprint: pre_checks      # Stack: [hash_deploy, hash_pre]
      # contains: blueprint: connectivity_test  → Stack: [hash_deploy, hash_pre, hash_ct]
  - name: apply_config         # Stack: [hash_deploy] (pre_checks popped)
  - blueprint: post_checks     # Stack: [hash_deploy, hash_post]
      # contains: blueprint: connectivity_test  → Stack: [hash_deploy, hash_post, hash_ct] (VALID)
```

**Invalid: Direct Circular**
```yaml
# blueprint_a.yaml
tasks:
  - blueprint: blueprint_b

# blueprint_b.yaml
tasks:
  - blueprint: blueprint_a  # Stack: [hash_a, hash_b] → trying to add hash_a → CIRCULAR!
```

**Invalid: Indirect Circular**
```yaml
# blueprint_a.yaml
tasks:
  - blueprint: blueprint_b

# blueprint_b.yaml
tasks:
  - blueprint: blueprint_c

# blueprint_c.yaml
tasks:
  - blueprint: blueprint_a  # Stack: [hash_a, hash_b, hash_c] → trying to add hash_a → CIRCULAR!
```

## 4. Content-Based Blueprint Identity

### 4.1 The Problem with Path-Based Identity

File paths are fragile identifiers. The same blueprint can be referenced via:
- Catalog name: `health_check`
- Relative path: `../blueprints/health_check.yaml`
- Absolute path: `/project/blueprints/health_check.yaml`

Additionally, identical content may exist in multiple locations (copies, backups).

### 4.2 Content Hash Solution

A utility function in utils.py provides content-based hashing:

```python
def _get_file_content_hash(file_path: Path) -> str:
    """
    Generate a stable hash from file content for identity comparison.
    
    Normalizes YAML content before hashing to ensure equivalent content
    produces the same hash regardless of formatting differences.
    
    Args:
        file_path: Path to the file to hash.
        
    Returns:
        A 16-character hex string representing the content hash.
    """
    content = file_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    normalized = yaml.dump(data, sort_keys=True, default_flow_style=False)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
```

### 4.3 Benefits

1. **Robust Circular Detection**: Same content via different paths is recognized as identical
2. **Duplicate Detection**: Identical blueprints in multiple locations produce the same hash
3. **Parse Once**: Content cache uses hash as key, avoiding redundant parsing
4. **Platform Independent**: Works consistently across operating systems

## 5. Exception Hierarchy

### 5.1 Blueprint Exceptions

Two exception classes provide clear, actionable error messages:

```python
class BlueprintError(WorkflowError):
    """Base exception for all blueprint-related errors."""
    
    def __init__(
        self, 
        message: str = "", 
        blueprint_name: str = "", 
        details: dict[str, Any] | None = None
    ):
        self.blueprint_name = blueprint_name
        self.details = details or {}
        prefix = f"Blueprint '{blueprint_name}': " if blueprint_name else "Blueprint: "
        super().__init__(f"{prefix}{message}")


class BlueprintCircularDependencyError(BlueprintError):
    """Raised when circular dependencies are detected in blueprint expansion."""
    
    def __init__(self, blueprint_name: str, dependency_chain: list[str]):
        self.dependency_chain = dependency_chain
        chain_str = " → ".join(dependency_chain)
        super().__init__(
            message=f"Circular dependency detected: {chain_str} → {blueprint_name}",
            blueprint_name=blueprint_name,
            details={"dependency_chain": dependency_chain}
        )
```

### 5.2 Error Scenarios

```python
# Not found
raise BlueprintError(
    "Not found in catalog or filesystem",
    blueprint_name="missing_bp",
    details={"searched_locations": ["blueprints/", "./missing_bp.yaml"]}
)

# Invalid structure
raise BlueprintError(
    "Invalid structure: missing 'tasks' key",
    blueprint_name="bad_blueprint.yaml"
)

# Invalid task definition
raise BlueprintError(
    "Task must have either 'name' or 'blueprint', not both/neither",
    blueprint_name="malformed.yaml",
    details={"keys_found": ["args", "hooks"]}
)

# Circular dependency
raise BlueprintCircularDependencyError(
    "ospf_config", 
    ["a3f2c8d9", "b7e4f1a2", "c9d8e7f6"]
)

# Template resolution error (blueprint reference)
raise WorkflowError(
    "Failed to resolve blueprint reference '{{ env }}_checks': "
    "Variable 'env' not found. Available variables: workflow_name, region, device_type"
)

# Template resolution error (if condition)
raise WorkflowError(
    "Failed to evaluate blueprint 'if' condition '{{ env == \"prod\" }}': "
    "Variable 'env' not found. Available variables: workflow_name, region, device_type"
)

# Invalid condition type
raise WorkflowError(
    "Blueprint 'if' condition must be boolean or string, got list"
)
```

## 6. Blueprint Resolution Architecture

### 6.1 Resolution Order

Blueprints are resolved through a two-tier hierarchy:

1. **Cataloged Blueprints**: Named blueprints discovered from `local_blueprints` directories
2. **File Paths**: Direct file references (relative or absolute)

### 6.2 Blueprint Syntax

```yaml
# Regular task - has 'name' key
- name: gather_facts
  args:
    gather_subset: hardware

# Blueprint reference - has 'blueprint' key, NO 'name' key
- blueprint: configure_ospf

# Dynamic blueprint reference using assembly-time variables
- blueprint: "{{ env }}_validation"

# Conditional blueprint reference (static boolean)
- blueprint: configure_ospf
  if: true

# Conditional blueprint with Jinja2 expression
- blueprint: staging_procedures
  if: "{{ env == 'staging' }}"

# Conditional blueprint with variable check
- blueprint: rollback_procedures
  if: "{{ enable_rollback }}"

# Combined: Dynamic reference AND conditional inclusion
- blueprint: "{{ env }}_{{ validation_level }}_checks"
  if: "{{ env == 'prod' }}"

# Invalid - both keys present
- name: some_task
  blueprint: some_blueprint  # ERROR!

# Invalid - neither key present
- args:
    some: value  # ERROR!

# Invalid - 'if' without blueprint or name
- if: "{{ condition }}"  # ERROR!
```

### 6.3 Resolution Implementation

```python
@classmethod
def _resolve_blueprint_to_path(cls, blueprint_ref: str) -> Path:
    """
    Resolve blueprint reference to file path.
    
    Resolution order:
    1. Catalog lookup (by name)
    2. Direct file path (relative or absolute)
    
    Args:
        blueprint_ref: Blueprint name or file path (already template-resolved).
        
    Returns:
        Resolved file path.
        
    Raises:
        BlueprintError: If blueprint cannot be found.
    """
    # Check catalog first
    if blueprint_ref in cls._get_blueprints_catalog():
        return cls._get_blueprints_catalog()[blueprint_ref]
    
    # Try as file path
    path = Path(blueprint_ref)
    
    if path.is_absolute() and path.exists():
        return path
    
    # Relative to current working directory
    resolved = Path.cwd() / path
    if resolved.exists():
        return resolved
    
    # Try with .yaml extension
    if not path.suffix:
        resolved_yaml = Path.cwd() / f"{path}.yaml"
        if resolved_yaml.exists():
            return resolved_yaml
    
    raise BlueprintError(
        "Not found in catalog or filesystem",
        blueprint_name=blueprint_ref,
        details={
            "searched_locations": [
                f"Catalog: {list(cls._get_blueprints_catalog().keys())[:5]}...",
                str(Path.cwd() / path),
                str(Path.cwd() / f"{path}.yaml"),
            ]
        }
    )
```

## 7. Integration Architecture

### 7.1 Settings Integration

```python
# settings.py
class NornFlowSettings(BaseSettings):
    local_blueprints: list[str] = Field(
        default=["blueprints"],
        description="Directories containing blueprint definitions"
    )
```

### 7.2 Catalog Integration

```python
# nornflow.py
class NornFlow:
    def _initialize_catalogs(self) -> None:
        """Initialize all catalogs including blueprints."""
        self._blueprints_catalog = FileCatalog("blueprints")
    
    def _load_blueprints_catalog(self) -> None:
        """Discover blueprint files from configured directories."""
        for directory in self.settings.local_blueprints:
            count = self._blueprints_catalog.discover_items_in_dir(
                directory,
                predicate=is_blueprint_file,
                recursive=True
            )
            logger.info(f"Discovered {count} blueprints in {directory}")
```

### 7.3 WorkflowModel Integration

```python
@classmethod
def create(cls, dict_args: dict[str, Any], *args: Any, **kwargs: Any) -> "WorkflowModel":
    """
    Create WorkflowModel with blueprint expansion.
    
    Args:
        dict_args: Workflow definition dictionary.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments, including blueprint expansion services.
        
    Returns:
        Initialized WorkflowModel with expanded tasks.
    """
    dict_args = dict_args.pop("workflow")
    
    # Delegate blueprint expansion to external service
    blueprint_expander = kwargs.get("blueprint_expander")
    if blueprint_expander:
        expanded_tasks = blueprint_expander.expand_blueprints(
            dict_args["tasks"],
            blueprints_catalog=kwargs.get("blueprints_catalog"),
            vars_dir=kwargs.get("vars_dir"),
            workflow_path=kwargs.get("workflow_path"),
            workflow_roots=kwargs.get("workflow_roots"),
            inline_vars=dict_args.get("vars"),
        )
        dict_args["tasks"] = expanded_tasks
    
    # Create TaskModels with sequential IDs
    tasks = []
    for task_dict in expanded_tasks:
        task = TaskModel.create(task_dict)
        tasks.append(task)
    
    dict_args["tasks"] = tasks
    return super().create(dict_args, *args, **kwargs)
```

### 7.4 Variable Context Builder

```python
# nornflow/blueprints/resolver.py
class BlueprintResolver:
    """Handles blueprint template resolution and context building."""
    
    def build_resolution_context(
        self,
        vars_dir: Path,
        workflow_path: Path | None,
        workflow_roots: list[str],
        inline_workflow_vars: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build variable context for blueprint resolution."""
        context = self._load_env_vars()
        defaults_path = vars_dir / "defaults.yaml"
        if defaults_path.exists():
            try:
                context.update(load_file_to_dict(defaults_path))
            except Exception:
                pass

        if workflow_path:
            domain_defaults = self._load_domain_defaults(vars_dir, workflow_path, workflow_roots)
            context.update(domain_defaults)

        if inline_workflow_vars:
            context.update(inline_workflow_vars)
        return context
```

### 7.5 Template Resolution

```python
# nornflow/vars/jinja2_utils.py
class Jinja2EnvironmentManager:
    """Manages Jinja2 environment creation and template rendering."""
    
    def render_template(self, template_str: str, context: dict[str, Any], error_context: str) -> str:
        """Render Jinja2 template with error handling."""
        try:
            env = Environment(undefined=StrictUndefined)
            template = env.from_string(template_str)
            return template.render(context)
        except UndefinedError as e:
            raise BlueprintError(f"Undefined variable in blueprint {error_context}: {e}") from e
        except TemplateSyntaxError as e:
            raise BlueprintError(f"Syntax error in blueprint {error_context}: {e}") from e
```

### 7.6 Condition Evaluation

```python
# nornflow/blueprints/resolver.py
class BlueprintResolver:
    """Handles blueprint template resolution and context building."""
    
    def evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate blueprint condition."""
        result = self.jinja2_manager.render_template(f"{{{{ {condition} }}}}", context, "condition")
        return result.lower() in ('true', '1', 'yes')
```

### 7.7 Utility Function

```python
# utils.py
def _get_file_content_hash(file_path: Path) -> str:
    """
    Generate a stable hash from file content for identity comparison.
    
    Normalizes YAML content before hashing to ensure equivalent content
    produces the same hash regardless of formatting differences.
    
    Args:
        file_path: Path to the file to hash.
        
    Returns:
        A 16-character hex string representing the content hash.
        
    Raises:
        ResourceError: If file cannot be read or parsed.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        normalized = yaml.dump(data, sort_keys=True, default_flow_style=False)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    except Exception as e:
        raise ResourceError(
            f"Failed to hash file content: {e}",
            resource_type="file",
            resource_name=str(file_path)
        ) from e
```

## 8. Task ID Assignment Preservation

The expansion maintains correct ID sequencing:

```yaml
# Input workflow
tasks:
  - name: pre_check        # → ID 1
  - blueprint: ospf_setup   # Contains 2 tasks → IDs 2, 3
  - name: post_validation  # → ID 4

# Blueprint 'ospf_setup'
tasks:
  - name: configure_ospf   # → ID 2
  - name: verify_ospf      # → ID 3
```

**After Expansion**:
```python
[
    TaskModel(id=1, name="pre_check"),
    TaskModel(id=2, name="configure_ospf"),
    TaskModel(id=3, name="verify_ospf"),
    TaskModel(id=4, name="post_validation")
]
```

## 9. Dynamic Blueprint Resolution

### 9.1 Assembly-Time Variable Context

Blueprint references and conditional inclusion can use Jinja2 templates with variables available at **workflow assembly time**. This provides dynamic blueprint selection and inclusion control while maintaining compile-time expansion.

**Available Variable Sources**:

1. **Environment Variables**: `NORNFLOW_VAR_*` environment variables
2. **Domain Defaults**: Variables from `defaults.yaml` files
3. **Workflow Variables**: Variables defined in the workflow definition
4. **CLI Variables**: Variables provided via command-line or NornFlow initialization

**Not Available**:
- Host-specific variables (e.g., `host.name`, `host.data.*`)
- Runtime variables (generated during task execution)
- Task result variables

### 9.2 Variable Precedence

Variables are layered with increasing precedence:

```
Environment Variables (lowest)
    ↓
Domain Defaults
    ↓
Workflow Variables
    ↓
CLI Variables (highest)
```

### 9.3 Template Resolution Examples

**Environment-Based Blueprint Selection**:
```yaml
# Set via: export NORNFLOW_VAR_ENV=prod
workflow:
  name: "Deploy Configuration"
tasks:
  - blueprint: "{{ env }}_validation"  # Resolves to: prod_validation
  - name: deploy_config
  - blueprint: "{{ env }}_post_checks"  # Resolves to: prod_post_checks
```

**Conditional Blueprint Selection (Static)**:
```yaml
workflow:
  name: "Site Deployment"
  vars:
    deploy_type: "full"
    
tasks:
  # Dynamic reference
  - blueprint: "{{ 'comprehensive_checks' if deploy_type == 'full' else 'basic_checks' }}"
  - name: apply_configuration
```

**Conditional Blueprint Inclusion (Separate `if` field)**:
```yaml
workflow:
  name: "Environment-Aware Deployment"
  vars:
    env: "staging"
    enable_rollback: true
    
tasks:
  # Conditionally include blueprints based on environment
  - blueprint: staging_procedures
    if: "{{ env == 'staging' }}"
  
  - blueprint: prod_procedures
    if: "{{ env == 'prod' }}"
  
  # Conditionally include based on feature flag
  - blueprint: rollback_procedures
    if: "{{ enable_rollback }}"
  
  - name: deploy_application
```

**Combined: Dynamic Reference AND Conditional Inclusion**:
```yaml
workflow:
  vars:
    env: "prod"
    validation_level: "strict"
    enable_monitoring: true
    
tasks:
  # Dynamic reference with condition
  - blueprint: "{{ env }}_{{ validation_level }}_checks"
    if: "{{ env == 'prod' }}"
  
  - name: deploy_config
  
  # Another dynamic reference with different condition
  - blueprint: "{{ env }}_monitoring_setup"
    if: "{{ enable_monitoring }}"
```

**Region-Based Blueprint Selection**:
```yaml
# CLI: nornflow run workflow.yaml --vars region=us-east
workflow:
  name: "Regional Deployment"
  
tasks:
  - blueprint: "{{ region }}_prerequisites"
  - blueprint: "global_health_check"
  - blueprint: "{{ region }}_configuration"
  - blueprint: "{{ region }}_validation"
  - blueprint: "global_post_checks"
```

**Complex Conditional Logic**:
```yaml
workflow:
  vars:
    env: "prod"
    enable_backups: true
    enable_monitoring: true
    critical_deployment: false
    
tasks:
  - blueprint: "{{ env }}_health_check"
  
  - blueprint: backup_config
    if: "{{ enable_backups }}"
  
  - blueprint: "{{ env }}_{{ 'strict' if env == 'prod' else 'lenient' }}_validation"
    if: "{{ not critical_deployment }}"
  
  - name: deploy
  
  - blueprint: monitoring_setup
    if: "{{ enable_monitoring and env == 'prod' }}"
```

### 9.4 Resolution Process Flow

```
1. WorkflowModel.create() invoked
2. Build assembly-time variable context:
   - Load environment variables (NORNFLOW_VAR_*)
   - Load domain defaults (defaults.yaml)
   - Merge workflow vars
   - Merge CLI vars
3. For each task in task list:
   - If has 'blueprint' key:
     a. Evaluate 'if' condition (if present) using var context
     b. Skip to next item if condition is false
     c. Resolve Jinja2 template in blueprint reference using var context
     d. Resolve to file path (catalog or filesystem)
     e. Get content hash
     f. Check for circular dependency
     g. Recursively expand (passing var context)
   - If has 'name' key:
     a. Pass through unchanged
4. Create TaskModel instances from expanded list
```

### 9.5 Error Handling

**Undefined Variable (Blueprint Reference)**:
```python
# Blueprint reference: {{ missing_var }}_checks
# Error message:
WorkflowError: Failed to resolve blueprint reference '{{ missing_var }}_checks': 
Undefined variable 'missing_var'. Available variables: env, region, deploy_type, workflow_name
```

**Undefined Variable (If Condition)**:
```python
# If condition: {{ missing_var == 'prod' }}
# Error message:
WorkflowError: Failed to evaluate blueprint 'if' condition '{{ missing_var == "prod" }}': 
Undefined variable 'missing_var'. Available variables: env, region, deploy_type, workflow_name
```

**Template Syntax Error (Blueprint Reference)**:
```python
# Blueprint reference: {{ env _checks }}  # Missing closing brace
# Error message:
WorkflowError: Invalid Jinja2 syntax in blueprint reference '{{ env _checks }}': 
Expected '}}' at position 7
```

**Template Syntax Error (If Condition)**:
```python
# If condition: {{ env == prod }}  # Missing quotes
# Error message:
WorkflowError: Invalid Jinja2 syntax in blueprint 'if' condition '{{ env == prod }}': 
'prod' is undefined
```

**Blueprint Not Found (After Resolution)**:
```python
# Resolved to: production_validation
# Error message:
BlueprintError: Blueprint 'production_validation': Not found in catalog or filesystem.
Details: {
  'searched_locations': [
    'Catalog: [dev_validation, test_validation, ...]',
    '/project/production_validation',
    '/project/production_validation.yaml'
  ]
}
```

**Invalid Condition Type**:
```python
# If condition is a list
# Error message:
WorkflowError: Blueprint 'if' condition must be boolean or string, got list
```

### 9.6 Best Practices

1. **Use Descriptive Variable Names**: Make template logic clear
   ```yaml
   # Good
   - blueprint: "{{ environment }}_{{ validation_level }}_checks"
   
   # Avoid
   - blueprint: "{{ e }}_{{ v }}_checks"
   ```

2. **Provide Sensible Defaults**: Use workflow vars as fallbacks
   ```yaml
   workflow:
     vars:
       env: "dev"  # Default value
       
   tasks:
     - blueprint: "{{ env }}_validation"  # Works even if ENV not set
   ```

3. **Document Variable Requirements**: Comment expected variables
   ```yaml
   workflow:
     # Expects: NORNFLOW_VAR_REGION or --vars region=<value>
     # Valid regions: us-east, us-west, eu-central
     name: "Regional Deployment"
     
   tasks:
     - blueprint: "{{ region }}_checks"
   ```

4. **Keep Templates Simple**: Complex logic in blueprints, not references
   ```yaml
   # Good: Simple selection
   - blueprint: "{{ 'strict' if env == 'prod' else 'basic' }}_validation"
   
   # Avoid: Complex nested logic in reference
   - blueprint: "{{ 'strict' if env == 'prod' and region == 'us-east' and critical else 'basic' }}_validation"
   ```

5. **Use Separate `if` for Complex Conditions**: Improves readability
   ```yaml
   # Good: Separate concerns
   - blueprint: "{{ env }}_validation"
     if: "{{ env == 'prod' and enable_strict_checks }}"
   
   # Avoid: Mixing concerns
   - blueprint: "{{ 'prod_strict' if env == 'prod' and enable_strict_checks else 'basic' }}_validation"
   ```

6. **Test Variable Combinations**: Verify all expected paths work
   ```bash
   # Test different environments
   NORNFLOW_VAR_ENV=dev nornflow run workflow.yaml
   NORNFLOW_VAR_ENV=staging nornflow run workflow.yaml
   NORNFLOW_VAR_ENV=prod nornflow run workflow.yaml
   ```

7. **Validate Blueprint Existence**: Ensure all possible resolved names exist
   ```yaml
   # If you use {{ env }}_validation, ensure these blueprints exist:
   # - dev_validation.yaml
   # - staging_validation.yaml
   # - prod_validation.yaml
   ```

## 10. Variable System Integration

### 10.1 Variable Inheritance

Blueprints inherit the complete variable context:
- No blueprint-specific variable passing
- All workflow variables available to blueprint tasks
- Standard NornFlow variable precedence applies

### 10.2 Variable Resolution

```yaml
# workflow.yaml
workflow:
  name: "Network Config"
  vars:
    ospf_area: 0
    ospf_process: 1

tasks:
  - blueprint: configure_ospf

# blueprints/configure_ospf.yaml
tasks:
  - name: netmiko_send_config
    args:
      config_commands:
        - "router ospf {{ ospf_process }}"
        - "network {{ host.data.network }} area {{ ospf_area }}"
```

## 11. Usage Patterns

### 11.1 Basic Blueprint

```yaml
# blueprints/interface_shutdown.yaml
tasks:
  - name: netmiko_send_config
    args:
      config_commands:
        - "interface {{ interface_name }}"
        - "shutdown"
        - "description SHUT BY AUTOMATION"
  
  - name: napalm_validate
    args:
      validation_source: "validations/interface_down.yaml"
```

### 11.2 Nested Blueprint

```yaml
# blueprints/full_ospf_deployment.yaml
tasks:
  - blueprint: prepare_routing
  - blueprint: configure_ospf
  - blueprint: verify_ospf
  - name: save_config
```

### 11.3 Repeated Blueprint Use

```yaml
# workflows/change_window.yaml
workflow:
  name: "Change Window with Health Checks"

tasks:
  - blueprint: health_check
  
  - name: apply_configuration
  
  - blueprint: health_check
  
  - name: save_running_config
  
  - blueprint: health_check
```

### 11.4 Dynamic Blueprint Selection with Conditional Inclusion

```yaml
# workflows/environment_aware_deployment.yaml
workflow:
  name: "Environment-Aware Deployment"
  vars:
    env: "staging"
    enable_rollback: true
    enable_monitoring: false
    
tasks:
  # Dynamic reference with conditional inclusion
  - blueprint: "{{ env }}_pre_validation"
    if: "{{ env in ['staging', 'prod'] }}"
  
  # Conditional inclusion with static reference
  - blueprint: backup_config
    if: "{{ enable_rollback }}"
  
  - name: deploy_configuration
  
  # Combined: dynamic reference and condition
  - blueprint: "{{ env }}_{{ 'comprehensive' if env == 'prod' else 'basic' }}_validation"
    if: "{{ env == 'prod' }}"
  
  # Another conditional blueprint
  - blueprint: monitoring_setup
    if: "{{ enable_monitoring }}"
  
  - name: finalize_deployment
```

### 11.5 Region-Based Deployment

```yaml
# workflows/multi_region_deployment.yaml
# Run with: nornflow run workflow.yaml --vars region=us-east
workflow:
  name: "Multi-Region Deployment"
  
tasks:
  - blueprint: "{{ region }}_prerequisites"
  - blueprint: "global_health_check"
  - blueprint: "{{ region }}_configuration"
  - blueprint: "{{ region }}_validation"
  - blueprint: "global_post_checks"
```

### 11.6 Workflow Using Mixed Sources and Conditions

```yaml
# workflows/site_deployment.yaml
workflow:
  name: "Site Deployment"
  vars:
    site_id: "NYC01"
    deploy_mode: "cautious"
    is_production: false
    
tasks:
  - name: gather_facts
  
  - blueprint: base_configuration
  
  - blueprint: "../shared/blueprints/security_hardening.yaml"
    if: "{{ is_production }}"
  
  - blueprint: "{{ deploy_mode }}_validation"
  
  - blueprint: site_specific_config
  
  - name: final_validation
    args:
      validation_file: "{{ site_id }}_validation.yaml"
```

### 11.7 Environment-Specific Blueprint Composition

```yaml
# workflows/tiered_deployment.yaml
workflow:
  name: "Tiered Environment Deployment"
  vars:
    env: "dev"
    
tasks:
  # Different blueprints for different environments
  - blueprint: dev_quick_checks
    if: "{{ env == 'dev' }}"
  
  - blueprint: staging_moderate_checks
    if: "{{ env == 'staging' }}"
  
  - blueprint: prod_comprehensive_checks
    if: "{{ env == 'prod' }}"
  
  # Common deployment step
  - name: deploy_application
  
  # Environment-specific post-deployment
  - blueprint: dev_simple_validation
    if: "{{ env == 'dev' }}"
  
  - blueprint: staging_full_validation
    if: "{{ env == 'staging' }}"
  
  - blueprint: prod_comprehensive_validation
    if: "{{ env == 'prod' }}"
```

## 12. Error Handling

### 12.1 Clear Error Messages

```python
# Circular dependency
BlueprintCircularDependencyError: 
  Blueprint 'ospf_config': Circular dependency detected: 
    a3f2c8d9 → b7e4f1a2 → c9d8e7f6 → ospf_config

# Not found
BlueprintError: 
  Blueprint 'missing_bp': Not found in catalog or filesystem
  Details: {
    'searched_locations': [
      'Catalog: [ospf_config, bgp_config, ...]',
      '/project/missing_bp',
      '/project/missing_bp.yaml'
    ]
  }

# Invalid structure
BlueprintError: 
  Blueprint 'bad_blueprint.yaml': Invalid structure: missing 'tasks' key

# Template resolution error (blueprint reference)
WorkflowError:
  Failed to resolve blueprint reference '{{ env }}_validation': 
  Undefined variable 'env'. Available variables: region, deploy_type, workflow_name

# Template resolution error (if condition)
WorkflowError:
  Failed to evaluate blueprint 'if' condition '{{ env == "prod" }}':
  Undefined variable 'env'. Available variables: region, deploy_type, workflow_name

# Invalid condition type
WorkflowError:
  Blueprint 'if' condition must be boolean or string, got list
```

### 12.2 Validation Points

1. **Catalog Discovery**: Validate blueprint files exist and are readable
2. **Load Time**: Validate YAML structure and required keys
3. **Condition Evaluation**: Validate boolean/string types and evaluate expressions
4. **Template Resolution**: Validate Jinja2 syntax and variable availability
5. **Expansion Time**: Detect circular dependencies via content-hash stack
6. **Task Creation**: Standard TaskModel validation applies

## 13. Design Rationale Summary

| Decision | Rationale |
|----------|-----------|
| Compile-time expansion | Preserves execution model, zero runtime overhead |
| Dynamic template resolution | Enables environment-specific deployments while maintaining compile-time philosophy |
| Conditional blueprint inclusion | Provides flexible workflow composition based on assembly-time context |
| Assembly-time variables only | Clear separation: assembly vs execution contexts |
| Separate `if` field | Clean syntax, explicit intent, easier to read and maintain |
| No blueprint-specific vars | Simplicity, consistent variable model |
| Nested blueprint support | Enables modular, composable designs |
| Path-based circular detection | Allows repeated use while preventing infinite loops |
| Content-based identity | Robust detection regardless of reference method |
| Two exceptions only | Simple hierarchy: general errors + circular dependency |
| Similar to `import_tasks` | Static expansion aligns with Ansible's proven pattern |

## 14. Refactored Architecture Overview

### 14.1 Separation of Concerns

To improve maintainability and reduce coupling, the blueprint feature has been refactored into a modular architecture:

**Before (Monolithic)**:
- All blueprint logic in `workflow.py`
- Jinja2 management scattered across modules
- Tight coupling between model and implementation

**After (Modular)**:
- **Blueprint Package** (`nornflow/blueprints/`): Dedicated to blueprint expansion, resolution, and validation
- **Centralized Jinja2** (`nornflow/vars/jinja2_utils.py`): Shared Jinja2 environment management
- **WorkflowModel**: Focused on model responsibilities, delegates expansion to services

### 14.2 Package Structure

```
nornflow/
├── blueprints/           # New: Blueprint-specific logic
│   ├── __init__.py
│   ├── expander.py       # BlueprintExpander class
│   └── resolver.py       # BlueprintResolver class
├── vars/
│   ├── jinja2_utils.py   # New: Jinja2EnvironmentManager
│   └── ...               # Existing variable system
├── models/
│   ├── workflow.py       # Updated: Delegates to BlueprintExpander
│   └── ...               # Other models
└── ...                   # Other modules
```

### 14.3 Service-Based Integration

WorkflowModel now uses dependency injection for blueprint services:

```python
# In NornFlow initialization
jinja2_manager = Jinja2EnvironmentManager()
resolver = BlueprintResolver(jinja2_manager)
expander = BlueprintExpander(resolver)

# Pass to WorkflowModel.create()
WorkflowModel.create(
    workflow_dict,
    blueprint_expander=expander,
    blueprints_catalog=catalog,
    # ... other params
)
```

### 14.4 Benefits of Refactoring

1. **Separation of Concerns**: Blueprint logic isolated from model logic
2. **Reusability**: Jinja2 utilities available for other features
3. **Testability**: Each component can be unit tested independently
4. **Maintainability**: Changes to blueprint logic don't affect core models
5. **Extensibility**: Easy to add new blueprint features without touching workflow.py

## 15. Implementation Roadmap

### Phase 1: Core Infrastructure Setup (Updated)
**Goal**: Establish the foundational settings and catalog integration for blueprints.

**Changes Required**:

1. **Update settings.py**
   - Add `local_blueprints: list[str]` field with default `["blueprints"]`
   - Field should follow existing patterns for catalog directory lists

2. **Update utils.py**
   - Add `_get_file_content_hash(file_path: Path) -> str` function
   - Implement YAML normalization and SHA256 hashing
   - Raise `ResourceError` on file read/parse failures

3. **Update nornflow.py**
   - Add `_blueprints_catalog: FileCatalog` to `__init__`
   - Implement catalog initialization in `_initialize_catalogs()`
   - Add `is_blueprint_file()` predicate function (similar to existing predicates)
   - Implement blueprint catalog loading in `_load_catalog()` method

**Testing Focus**: Catalog discovery, file hashing, settings validation

**Dependencies**: None (foundational layer)

---

### Phase 2: Exception Hierarchy (Updated)
**Goal**: Define clear exception types for blueprint-specific errors.

**Changes Required**:

1. **Update exceptions.py**
   - Add `BlueprintError(WorkflowError)` class
   - Add `BlueprintCircularDependencyError(BlueprintError)` class
   - Both should include `blueprint_name` and `details` attributes
   - Implement clear, actionable error messages

**Testing Focus**: Exception instantiation, message formatting, attribute access

**Dependencies**: None

---

### Phase 3: Centralized Jinja2 Management (New)
**Goal**: Create shared Jinja2 utilities for blueprint resolution and other features.

**Changes Required**:

1. **Create nornflow/vars/jinja2_utils.py**
   - Add `Jinja2EnvironmentManager` class
   - Implement `render_template()` method with error handling
   - Support StrictUndefined for template validation

**Testing Focus**: Template rendering, error handling, undefined variable detection

**Dependencies**: Phase 2 (exceptions for error handling)

---

### Phase 4: Blueprint Package Creation (New)
**Goal**: Extract blueprint logic into dedicated package.

**Changes Required**:

1. **Create nornflow/blueprints/__init__.py**
   - Export `BlueprintExpander` and `BlueprintResolver`

2. **Create nornflow/blueprints/resolver.py**
   - Add `BlueprintResolver` class
   - Implement variable context building
   - Implement template resolution using `Jinja2EnvironmentManager`
   - Implement condition evaluation

3. **Create nornflow/blueprints/expander.py**
   - Add `BlueprintExpander` class
   - Implement recursive blueprint expansion
   - Implement circular dependency detection
   - Implement blueprint validation and loading

**Testing Focus**: 
- Variable context building
- Template resolution
- Condition evaluation
- Blueprint expansion
- Circular detection
- Validation

**Dependencies**: Phase 1 (catalog), Phase 2 (exceptions), Phase 3 (Jinja2 utils)

---

### Phase 5: WorkflowModel Refactoring (New)
**Goal**: Simplify WorkflowModel by delegating blueprint expansion to services.

**Changes Required**:

1. **Update workflow.py**
   - Remove blueprint expansion methods
   - Update `create()` to accept `blueprint_expander` parameter
   - Delegate expansion to the injected service
   - Keep only model-specific logic

**Testing Focus**: Workflow creation with blueprint expansion, service integration

**Dependencies**: Phase 4 (blueprint package)

---

### Phase 6: Integration and Wiring (Updated)
**Goal**: Wire blueprint expansion into workflow creation process with variable context.

**Changes Required**:

1. **Update nornflow.py**
   - Initialize `Jinja2EnvironmentManager`, `BlueprintResolver`, `BlueprintExpander`
   - Pass expander to `WorkflowModel.create()`
   - Ensure CLI vars are passed correctly

2. **Update CLI integration** (if needed)
   - Ensure CLI vars are passed to `WorkflowModel.create()` as `cli_vars`
   - May require changes to run.py

**Testing Focus**: 
- End-to-end workflow loading with blueprints
- Variable context building from all sources
- CLI variable integration
- Task ID sequencing

**Dependencies**: Phase 5 (refactored WorkflowModel)

---

### Phase 7: Comprehensive Testing (Updated)
**Goal**: Validate all scenarios and edge cases.

**Test Categories**:

1. **Unit Tests** (`tests/unit/test_blueprints.py`)
   - Basic single blueprint expansion
   - Dynamic blueprint selection with templates
   - Static conditional inclusion (boolean true/false)
   - Dynamic conditional inclusion (Jinja2 expressions)
   - Combined dynamic reference and conditional inclusion
   - Variable precedence (ENV < domain < workflow < CLI)
   - Nested blueprints (3+ levels)
   - Repeated sequential use
   - Direct circular dependency detection
   - Indirect circular dependency detection
   - Content-based identity matching
   - Blueprint not found errors
   - Invalid blueprint structure errors
   - Mixed name/blueprint key errors
   - Path resolution (catalog, relative, absolute)
   - Template syntax errors (reference and condition)
   - Undefined variable errors (reference and condition)
   - Invalid condition type errors

2. **Integration Tests** (`tests/integration/test_blueprint_workflows.py`)
   - Full workflow execution with blueprints
   - Variable inheritance in blueprints
   - Mixed blueprint sources (catalog + file paths)
   - Task ID preservation across expansion
   - Blueprint catalog discovery
   - Environment variable integration
   - Domain defaults integration
   - CLI variable integration
   - Complex template logic scenarios
   - Complex conditional logic scenarios
   - Environment-specific workflow composition

**Dependencies**: Phase 6 (complete implementation)

---

### Phase 8: Documentation (Updated)
**Goal**: Document the feature for end users.

**Changes Required**:

1. **Create `docs/blueprints_guide.md`**
   - Basic blueprint usage
   - Dynamic blueprint selection with variables
   - Conditional blueprint inclusion (static and dynamic)
   - Variable availability and precedence
   - Nested blueprint patterns
   - Repeated use examples
   - Template syntax and best practices
   - Conditional inclusion best practices
   - Error handling guide
   - Real-world deployment scenarios

2. **Update core_concepts.md**
   - Add "Blueprints" section
   - Explain compile-time expansion with dynamic resolution
   - Explain conditional inclusion
   - Compare to Ansible's `import_tasks`
   - Clarify assembly-time vs runtime variables

3. **Update quick_start.md**
   - Add simple blueprint example to getting started
   - Show basic dynamic blueprint selection
   - Show basic conditional inclusion

4. **Update nornflow_settings.md**
   - Document `local_blueprints` setting

5. **Update variables_basics.md**
   - Add section on assembly-time variables
   - Explain variable availability in blueprint references vs task args
   - Explain variable availability in blueprint conditions

**Dependencies**: Phase 7 (tested implementation)

---

### Implementation Notes

**Dynamic Resolution Decision**: Blueprint references and conditional inclusion support Jinja2 templates using assembly-time variables (environment, domain defaults, workflow, CLI). This provides practical flexibility for environment-specific workflow composition while maintaining the compile-time expansion philosophy. Host and runtime variables remain unavailable during blueprint resolution to preserve the execution model.

**Conditional Inclusion Design**: The `if` field provides explicit, readable control over blueprint inclusion. It's evaluated before blueprint reference resolution, allowing efficient skipping of unnecessary expansions. This is distinct from task-level `if` hooks which operate during execution with per-host context.

**Variable Context Clarity**: Clear documentation distinguishes between assembly-time variables (used for blueprint selection and inclusion) and execution-time variables (used in task arguments). This prevents confusion about variable availability.

**File Organization**: Blueprint code is now organized in a dedicated `nornflow/blueprints/` package, while Jinja2 utilities are centralized in `nornflow/vars/jinja2_utils.py`. This reflects the deep coupling with core systems (settings, catalogs, workflow model, variable system) while maintaining clean separation.

**Testing Strategy**: Each phase should be fully tested before moving to the next. Integration tests in Phase 7 validate the complete system working together, including all variable sources and conditional logic.

---

## 16. Conclusion

The Blueprint feature provides powerful task reusability through a carefully designed macro expansion system that:

- **Preserves** NornFlow's simple, linear execution model
- **Enables** dynamic blueprint selection using assembly-time variables
- **Supports** conditional blueprint inclusion using assembly-time variables
- **Allows** complex nested compositions with safety guarantees
- **Permits** repeated sequential use of the same blueprint
- **Maintains** zero runtime overhead through compile-time expansion
- **Integrates** seamlessly with existing variable and task systems
- **Provides** clear error messages with actionable details
- **Uses** content-based identity for robust circular detection
- **Clarifies** variable availability (assembly-time vs runtime contexts)
- **Enables** environment-specific workflow composition

The implementation aligns with NornFlow's philosophy as a specialized network automation tool—providing focused functionality comparable to Ansible's `import_tasks` while adding practical dynamic resolution and conditional inclusion capabilities for environment-aware deployments.