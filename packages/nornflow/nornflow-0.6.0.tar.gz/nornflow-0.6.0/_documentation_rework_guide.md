Collecting workspace informationAfter thoroughly analyzing the code and documentation, here's my comprehensive roadmap for updating the documentation to cover the new Blueprints feature:

---

## 📋 Documentation Update Roadmap for Blueprints Feature

### Analysis Summary

The Blueprints feature is a **significant addition** that enables:
- Reusable task collections that can be referenced across workflows
- Variable resolution with full precedence chain during assembly-time
- Conditional blueprint inclusion via `if` conditions
- Nested blueprint composition with circular dependency detection
- Dynamic blueprint selection using Jinja2 templates

This feature sits between **workflow composition** and **variable system**, making it a core architectural component that deserves comprehensive documentation.

---

## 🎯 Proposed Documentation Changes

### **1. Create New File: `blueprints_guide.md` ⭐ (HIGH PRIORITY)**

**Rationale:** Blueprints are complex enough to warrant dedicated documentation, similar to how hooks and variables have their own guides.

**Proposed Structure:**
```markdown
# Blueprints Guide

## Table of Contents
- Overview
- What Are Blueprints?
- When to Use Blueprints
- Creating Blueprints
  - Blueprint Structure
  - Blueprint Discovery
  - Blueprint Catalog
- Using Blueprints in Workflows
  - Basic Blueprint Reference
  - Conditional Inclusion
  - Nested Blueprints
  - Dynamic Blueprint Selection
- Variable Resolution in Blueprints
  - Assembly-Time vs Runtime
  - Variable Precedence for Blueprints
  - Using Variables in Blueprint References
- Advanced Patterns
  - Blueprint Composition Strategies
  - Avoiding Circular Dependencies
  - Blueprint Parameterization Patterns
- Best Practices
- Troubleshooting
- Examples
```

**Key Sections to Cover:**
- Clear distinction between assembly-time (blueprint expansion) vs runtime (task execution)
- How blueprints interact with the variable system (subset of variables available)
- Circular dependency detection mechanism
- Practical examples with increasing complexity

---

### **2. Update quick_start.md 📝 (MEDIUM PRIORITY)**

**Changes Needed:**

**Section: "Your First NornFlow Project" → "1. Initialize NornFlow"**
- Add blueprints to the list of created directories
- Add brief one-liner: "📁 blueprints - Reusable task collections"

**New Section: "Using Blueprints" (after "Using Variables")**
```markdown
## Using Blueprints

Blueprints are reusable collections of tasks that you can reference across workflows:

### Create a Blueprint

```yaml
# blueprints/network_checks.yaml
tasks:
  - name: check_version
    task: netmiko_send_command
    args:
      command_string: "show version"
  
  - name: check_interfaces
    task: netmiko_send_command
    args:
      command_string: "show interfaces status"
```

### Use in Workflow

```yaml
workflow:
  name: "Device Health Check"
  tasks:
    - blueprint: network_checks
    - name: save_results
      task: write_file
      args:
        filename: "results.txt"
```
```

**Update "Useful Commands" section:**
```bash
# Show available blueprints
nornflow show --blueprints
```

---

### **3. Update core_concepts.md 📝 (HIGH PRIORITY)**

**Changes Needed:**

**Update Table of Contents:**
Add new section after "Domains":
```markdown
- [Blueprints](#blueprints)
  - [What are Blueprints?](#what-are-blueprints)
  - [Blueprint Discovery](#blueprint-discovery)
  - [Blueprint vs Workflow](#blueprint-vs-workflow)
```

**Update "Project Structure" section:**
Add blueprints directory to the structure:
```markdown
my_project/
├── nornflow.yaml
├── nornir_config.yaml
├── inventory.yaml
├── blueprints/              # Reusable task collections
│   ├── backup_tasks.yaml
│   └── validation_tasks.yaml
├── workflows/
│   ├── backup/
│   │   └── daily_backup.yaml
```

**New Section: "Blueprints" (after "Domains" section):**
```markdown
## Blueprints

### What are Blueprints?

Blueprints are reusable collections of tasks that can be referenced within workflows. They enable:
- **Code Reuse**: Define common task sequences once, use them everywhere
- **Modularity**: Break complex workflows into composable pieces
- **Maintainability**: Update task sequences in one place
- **Conditional Composition**: Include blueprints based on conditions

Unlike workflows, blueprints:
- Contain ONLY a `tasks` list (no workflow metadata)
- Are referenced by name or path within workflows
- Support nested composition (blueprints can reference other blueprints)
- Are expanded during workflow loading (assembly-time)

### Blueprint Discovery

NornFlow automatically discovers blueprints from directories specified in `nornflow.yaml`:

```yaml
local_blueprints:
  - "blueprints"
  - "shared/blueprints"
```

Blueprints are cataloged by filename (without extension) and can be referenced by:
1. Name from catalog: `blueprint: network_checks`
2. Relative path: `blueprint: ../shared/validation.yaml`
3. Absolute path: `blueprint: /opt/blueprints/security.yaml`

### Blueprint vs Workflow

| Aspect | Blueprint | Workflow |
|--------|-----------|----------|
| Purpose | Reusable task collection | Complete automation definition |
| Structure | Only `tasks:` list | Full workflow definition with metadata |
| Usage | Referenced within workflows | Executed directly |
| Nesting | Can reference other blueprints | Cannot be nested |
| Variables | Uses assembly-time variable subset | Full runtime variable access |
```

**Update "Catalogs" section:**
Add blueprints catalog after workflows:
```markdown
### Blueprint Catalog

The blueprint catalog contains all discovered blueprint YAML files. Blueprints are discovered from directories specified in `local_blueprints`:

```yaml
# nornflow.yaml
local_blueprints:
  - "blueprints"
  - "../shared_blueprints"
```

All files with `.yaml` or `.yml` extensions in these directories (including subdirectories) are considered blueprints.
```

**Update "Catalog Discovery" section:**
Add blueprints to the list:
```markdown
**Discovery order:**
1. Built-in items are loaded first
2. Local directories are processed in the order specified
3. Each directory is searched recursively

**View catalogs:**
```bash
nornflow show --catalogs  # Shows tasks, filters, workflows, and blueprints
nornflow show --blueprints  # Show only blueprints
```
```

---

### **4. Update `variables_basics.md` 📝 (MEDIUM PRIORITY)**

**Changes Needed:**

**Update "Quick Overview" section:**
Add note about blueprint assembly-time variables:
```markdown
## Quick Overview

NornFlow provides a powerful variable system with two namespaces and two resolution contexts:

**Namespaces:**
1. **Default namespace** - Your workflow variables (direct access: `{{ variable_name }}`)
2. **Host namespace** - Nornir inventory data (prefixed access: `{{ host.variable_name }}`)

**Resolution Contexts:**
1. **Assembly-Time** - During workflow loading (used by blueprints)
2. **Runtime** - During task execution (used by tasks)

> **Note:** Blueprints only have access to a subset of variables during assembly-time. See the [Blueprints Guide](./blueprints_guide.md) for details.
```

**New Section: "Assembly-Time vs Runtime Variables" (after "Variable Sources")**
```markdown
## Assembly-Time vs Runtime Variables

NornFlow resolves variables in two distinct contexts:

### Assembly-Time Resolution (Blueprints)

When workflows are loaded, NornFlow expands blueprint references using a **subset** of available variables:

**Available at Assembly-Time:**
1. Environment Variables (`NORNFLOW_VAR_*`)
2. Global Defaults (`vars/defaults.yaml`)
3. Domain Defaults (`vars/{domain}/defaults.yaml`)
4. Workflow Variables (`workflow.vars`)
5. CLI Variables (`--vars`)

**NOT Available at Assembly-Time:**
- Runtime variables (set by `set` task or `set_to` hook)
- Host inventory data (`host.*` namespace)

**Example:**
```yaml
workflow:
  name: "Conditional Blueprint"
  vars:
    enable_validation: true
  tasks:
    - blueprint: validation_tasks
      if: "{{ enable_validation }}"  # ✓ Works (workflow var)
    
    - blueprint: "{{ selected_blueprint }}"  # ✓ Works (CLI var)
```

### Runtime Resolution (Tasks)

During task execution, ALL variables are available including runtime variables and host data.

See the Blueprints Guide for more details on assembly-time variable resolution.
```

---

### **5. Update `nornflow_settings.md` 📝 (HIGH PRIORITY)**

**Changes Needed:**

**Update Table of Contents:**
Add `local_blueprints` to the list under "Optional Settings"

**New Section under "Optional Settings":**
```markdown
### `local_blueprints`

- **Description**: List of paths to directories containing blueprint definitions. Blueprints are reusable task collections that can be referenced within workflows. The search is recursive, meaning all subdirectories will be searched. All files with `.yaml` or `.yml` extensions are considered blueprints. Both absolute and relative paths are supported.
- **Type**: list[str]
- **Default**: ["blueprints"]
- **Path Resolution**: 
  - When loaded through `NornFlowSettings.load`, relative paths resolve against the settings file directory
  - Direct instantiation leaves relative paths untouched, so they resolve against the runtime working directory
  - Absolute paths are used as-is
- **Example**:
  ```yaml
  local_blueprints:
    - "blueprints"
    - "../shared_blueprints"
    - "/opt/company/blueprints"
  ```
- **Environment Variable**: `NORNFLOW_SETTINGS_LOCAL_BLUEPRINTS`
- **Note**: Blueprints are expanded during workflow loading (assembly-time) and have access to a subset of the variable system. See the [Blueprints Guide](./blueprints_guide.md) for details.
```

**Update sample nornflow.yaml in the documentation:**
Add `local_blueprints` field to any example configurations shown

---

### **6. Update api_reference.md 📝 (MEDIUM PRIORITY)**

**Changes Needed:**

**Update "NornFlow Class" → "Properties" table:**
Add new row:
```markdown
| `blueprints_catalog` | `FileCatalog` | Registry of blueprint files (read-only) |
```

**Update "WorkflowModel.create()" method documentation:**
Add blueprint-related kwargs:
```markdown
**Args:**
- `dict_args`: Dictionary containing the full workflow data, must include 'workflow' key.
- `*args`: Additional positional arguments passed to parent create method.
- `**kwargs`: Additional keyword arguments:
  - `blueprints_catalog` (dict[str, Path] | None): Catalog mapping blueprint names to file paths
  - `vars_dir` (Path | None): Directory containing variable files
  - `workflow_path` (Path | None): Path to the workflow file
  - `workflow_roots` (list[str] | None): List of workflow root directories
  - `cli_vars` (dict[str, Any] | None): CLI variables with highest precedence

**Returns:**
- `WorkflowModel`: The created WorkflowModel instance with expanded blueprints.

**Raises:**
- `WorkflowError`: If 'workflow' key is not present in dict_args.
- `BlueprintError`: If blueprint expansion fails.
- `BlueprintCircularDependencyError`: If circular dependencies detected in blueprint references.
```

**New Section: "Blueprint System Classes"**
```markdown
## Blueprint System Classes

### BlueprintResolver

Handles variable context building and template resolution for blueprints.

```python
from nornflow.blueprints import BlueprintResolver
```

**Methods:**

#### `build_context(...) -> dict[str, Any]`
Build variable context for blueprint resolution with proper precedence.

#### `resolve_template(template_str: str, context: dict[str, Any]) -> str`
Resolve a Jinja2 template in blueprint reference.

#### `evaluate_condition(condition: str | bool, context: dict[str, Any]) -> bool`
Evaluate blueprint `if` condition.

### BlueprintExpander

Handles recursive blueprint expansion with circular dependency detection.

```python
from nornflow.blueprints import BlueprintExpander
```

**Methods:**

#### `expand_blueprints(...) -> list[dict[str, Any]]`
Expand blueprint references in tasks list, including nested blueprints.

**Raises:**
- `BlueprintError`: If blueprint expansion fails
- `BlueprintCircularDependencyError`: If circular dependency detected
```

---

### **7. Update `hooks_guide.md` 📝 (LOW PRIORITY)**

**Changes Needed:**

**Update "Hook-Driven Template Resolution" section:**
Add note about blueprints:
```markdown
> **Note on Blueprints:** Blueprint expansion happens during workflow loading (assembly-time), before any hook processing. Blueprint `if` conditions are evaluated using the `BlueprintResolver`, which is separate from hook-driven template resolution that occurs at runtime.
```

---

### **8. Minor Updates to Other Files 📝 (LOW PRIORITY)**

**jinja2_filters.md:**
- No changes needed (blueprints use same filters as tasks)

**failure_strategies.md:**
- No changes needed (strategies apply to tasks, not blueprint expansion)

---

## 📊 Priority Summary

| Priority | Files | Estimated Effort |
|----------|-------|------------------|
| **HIGH** | `blueprints_guide.md` (new), core_concepts.md, nornflow_settings.md | 4-6 hours |
| **MEDIUM** | quick_start.md, variables_basics.md, api_reference.md | 2-3 hours |
| **LOW** | hooks_guide.md | 30 minutes |

**Total Estimated Effort:** 6.5 - 9.5 hours

---

## 🎯 Recommended Execution Order

1. **Create `blueprints_guide.md`** - This will be the comprehensive reference
2. **Update core_concepts.md** - Establishes blueprints in the mental model
3. **Update nornflow_settings.md** - Documents configuration
4. **Update quick_start.md** - Provides practical introduction
5. **Update variables_basics.md** - Clarifies assembly-time vs runtime
6. **Update api_reference.md** - Documents API
7. **Minor updates** - Complete remaining files

---

## 💡 Additional Recommendations

1. **Cross-reference heavily** - Link between blueprints guide, variables guide, and core concepts
2. **Include workflow evolution example** - Show progression from inline tasks → blueprint extraction → nested blueprints
3. **Troubleshooting section** - Common errors like circular dependencies, missing variables at assembly-time
4. **Visual diagrams** - Showing blueprint expansion flow and variable resolution contexts
5. **Real-world examples** - Network device validation, multi-stage deployment, environment-specific configurations

---

Let me know which file you'd like me to start with, and I'll provide the complete updated content!