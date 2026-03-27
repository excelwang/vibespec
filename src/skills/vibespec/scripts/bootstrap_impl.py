#!/usr/bin/env python3
"""Generate a minimal implementation skeleton for specs-only repositories."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import indent

import validate


SKILL_ROOT = Path(__file__).resolve().parent.parent
COMMON_ASSETS = SKILL_ROOT / "assets" / "bootstrap" / "common"
SUPPORTED_TEST_EXTENSIONS = {".py", ".js", ".ts", ".go", ".rs", ".cs"}

LANGUAGE_ALIASES = {
    "python": "py",
    "py": "py",
    "javascript": "js",
    "js": "js",
    "typescript": "ts",
    "ts": "ts",
    "go": "go",
    "golang": "go",
    "rust": "rs",
    "rs": "rs",
    "csharp": "cs",
    "cs": "cs",
    "dotnet": "cs",
}

LANGUAGE_DISPLAY = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "go": "Go",
    "rs": "Rust",
    "cs": "C#",
}

SOURCE_EXT = {
    "py": ".py",
    "js": ".js",
    "ts": ".ts",
    "go": ".go",
    "rs": ".rs",
    "cs": ".cs",
}

TEST_EXT = {
    "py": ".py",
    "js": ".js",
    "ts": ".ts",
    "go": "_test.go",
    "rs": ".rs",
    "cs": ".cs",
}

COMMENT_PREFIX = {
    "py": "#",
    "js": "//",
    "ts": "//",
    "go": "//",
    "rs": "//",
    "cs": "//",
}


@dataclass
class ContractLeaf:
    item_id: str
    line: int
    body: str

    @property
    def test_name_slug(self) -> str:
        return snake_case(self.item_id.split(".")[-1])


@dataclass
class ContractSection:
    item_id: str
    section_name: str
    slug: str
    source_file: str
    line: int
    leafs: list[ContractLeaf] = field(default_factory=list)


@dataclass
class ModuleSpec:
    item_id: str
    kind: str
    module_slug: str
    symbol_name: str
    line: int
    summary: str
    l3_items: list[str] = field(default_factory=list)


@dataclass
class SpecModel:
    contract_sections: list[ContractSection]
    modules: list[ModuleSpec]
    contract_spec_path: str
    requires_service_entrypoint: bool


def normalize_lang(value: str) -> str:
    normalized = LANGUAGE_ALIASES.get((value or "").strip().lower())
    if not normalized:
        supported = ", ".join(sorted(LANGUAGE_ALIASES))
        raise SystemExit(f"Unsupported --lang `{value}`. Supported values: {supported}")
    return normalized


def snake_case(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_").lower() or "generated_item"


def kebab_case(value: str) -> str:
    return snake_case(value).replace("_", "-")


def pascal_case(value: str) -> str:
    words = re.split(r"[^A-Za-z0-9]+", value)
    if len(words) == 1 and re.search(r"[a-z][A-Z]", value):
        return re.sub(r"[^A-Za-z0-9]", "", value) or "GeneratedItem"
    cleaned = [word for word in words if word]
    if not cleaned:
        return "GeneratedItem"
    return "".join(part[:1].upper() + part[1:] for part in cleaned)


def sanitize_identifier(value: str, *, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", value)
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    return cleaned


def safe_distribution_name(value: str, *, fallback: str = "bootstrap") -> str:
    cleaned = kebab_case(value) or fallback
    if cleaned[0].isdigit():
        cleaned = f"{fallback}-{cleaned}"
    return cleaned


def safe_package_name(value: str, *, fallback: str = "bootstrap") -> str:
    return sanitize_identifier(snake_case(value), fallback=fallback)


def safe_namespace(value: str, *, fallback: str = "Bootstrap") -> str:
    return sanitize_identifier(pascal_case(value), fallback=fallback)


def first_meaningful_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[>\-*`#\s]+", "", line).strip()
        if line:
            return line
    return "Pending specification-mapped implementation."


def asset_text(name: str) -> str:
    path = COMMON_ASSETS / name
    return path.read_text(encoding="utf-8")


def render_gate_profile(contract_spec: str, black_box_glob: str, white_box_glob: str, run_commands: list[str]) -> str:
    template = asset_text("gate-profile.json.tmpl")
    return (
        template.replace("__BLACK_BOX_GLOB__", black_box_glob)
        .replace("__WHITE_BOX_GLOB__", white_box_glob)
        .replace("__CONTRACT_SPEC__", contract_spec)
        .replace("__RUN_COMMANDS_JSON__", json.dumps(run_commands, indent=2))
    )


def render_test_workflow(contracts_command: str, whitebox_command: str) -> str:
    template = asset_text("test-workflow.sh.tmpl")
    return (
        template.replace("__CONTRACTS_COMMAND__", indent(contracts_command, "  "))
        .replace("__WHITEBOX_COMMAND__", indent(whitebox_command, "  "))
    )


def iter_spec_files(specs_dir: Path) -> list[Path]:
    return [
        path
        for path in sorted(specs_dir.rglob("*.md"))
        if "build" not in path.parts and not path.name.startswith(".")
    ]


def build_spec_model(specs_dir: Path) -> SpecModel:
    parsed = []
    for spec_file in iter_spec_files(specs_dir):
        data = validate.parse_spec_file(spec_file)
        if data:
            parsed.append((spec_file, data))

    l1_files = [(path, data) for path, data in parsed if data["layer"] == 1]
    l2_files = [(path, data) for path, data in parsed if data["layer"] == 2]
    l3_files = [(path, data) for path, data in parsed if data["layer"] == 3]

    if not l1_files:
        raise SystemExit("No L1 contract specs were found under `specs/`.")
    if not l2_files:
        raise SystemExit("No L2 architecture specs were found under `specs/`.")
    if not l3_files:
        raise SystemExit("No L3 runtime specs were found under `specs/`.")

    contract_sections = collect_contract_sections(l1_files, specs_dir)
    modules = collect_modules(l2_files)
    attach_l3_items(modules, l3_files)
    requires_service_entrypoint = detect_service_entrypoint(l2_files, l3_files)

    if not contract_sections:
        raise SystemExit("No testable `CONTRACTS.*` sections were found in L1.")
    if not modules:
        raise SystemExit("No leaf `ROLES.*` or `COMPONENTS.*` items were found in L2.")

    contract_spec_path = str(l1_files[0][0].relative_to(specs_dir.parent))
    return SpecModel(
        contract_sections=contract_sections,
        modules=modules,
        contract_spec_path=contract_spec_path,
        requires_service_entrypoint=requires_service_entrypoint,
    )


def collect_contract_sections(l1_files: list[tuple[Path, dict]], repo_root: Path) -> list[ContractSection]:
    sections: list[ContractSection] = []
    seen_slugs: set[str] = set()
    for spec_file, data in l1_files:
        items = data["items"]
        l1_ids = {item_id for item_id in items if item_id.startswith("CONTRACTS.")}
        if not l1_ids:
            continue
        leaf_ids = {
            item_id
            for item_id in l1_ids
            if validate.is_testable_l1_contract(item_id, l1_ids)
        }
        section_ids = sorted(
            [item_id for item_id in l1_ids if item_id.count(".") == 1],
            key=lambda item_id: items[item_id]["line"],
        )
        for section_id in section_ids:
            leafs = [
                ContractLeaf(
                    item_id=leaf_id,
                    line=items[leaf_id]["line"],
                    body=items[leaf_id]["body"].strip(),
                )
                for leaf_id in sorted(
                    [leaf_id for leaf_id in leaf_ids if leaf_id.startswith(section_id + ".")],
                    key=lambda leaf_id: items[leaf_id]["line"],
                )
            ]
            if not leafs:
                continue
            section_name = section_id.split(".", 1)[1]
            slug = snake_case(section_name)
            if slug in seen_slugs:
                raise SystemExit(
                    f"Duplicate contract section slug `{slug}` derived from `{section_id}`. "
                    "Rename the L1 sections to make bootstrap deterministic."
                )
            seen_slugs.add(slug)
            sections.append(
                ContractSection(
                    item_id=section_id,
                    section_name=section_name,
                    slug=slug,
                    source_file=str(spec_file.relative_to(repo_root.parent)),
                    line=items[section_id]["line"],
                    leafs=leafs,
                )
            )
    return sections


def collect_modules(l2_files: list[tuple[Path, dict]]) -> list[ModuleSpec]:
    modules: list[ModuleSpec] = []
    seen_slugs: set[str] = set()
    for _spec_file, data in l2_files:
        items = data["items"]
        candidate_ids = [
            item_id
            for item_id in items
            if item_id.startswith("ROLES.") or item_id.startswith("COMPONENTS.")
        ]
        leaf_ids = [
            item_id
            for item_id in candidate_ids
            if not any(
                other_id.startswith(item_id + ".")
                for other_id in candidate_ids
                if other_id != item_id
            )
        ]
        for item_id in sorted(leaf_ids, key=lambda value: items[value]["line"]):
            raw_name = item_id.split(".")[-1]
            module_slug = snake_case(raw_name)
            if module_slug in seen_slugs:
                raise SystemExit(
                    f"Duplicate module slug `{module_slug}` derived from `{item_id}`. "
                    "Rename the L2 roles/components to make bootstrap deterministic."
                )
            seen_slugs.add(module_slug)
            modules.append(
                ModuleSpec(
                    item_id=item_id,
                    kind="role" if item_id.startswith("ROLES.") else "component",
                    module_slug=module_slug,
                    symbol_name=sanitize_identifier(raw_name, fallback=pascal_case(raw_name)),
                    line=items[item_id]["line"],
                    summary=first_meaningful_line(items[item_id]["body"]),
                )
            )
    return modules


def attach_l3_items(modules: list[ModuleSpec], l3_files: list[tuple[Path, dict]]) -> None:
    module_by_id = {module.item_id: module for module in modules}
    for _spec_file, data in l3_files:
        refs_by_source: dict[str, list[str]] = {}
        for ref in data.get("references", []):
            refs_by_source.setdefault(ref["source_id"], []).append(ref["id"])
        for source_id, referenced_ids in refs_by_source.items():
            for referenced_id in referenced_ids:
                module = module_by_id.get(referenced_id)
                if module and source_id not in module.l3_items:
                    module.l3_items.append(source_id)


def detect_service_entrypoint(l2_files: list[tuple[Path, dict]], l3_files: list[tuple[Path, dict]]) -> bool:
    service_signals = (
        "standalone service",
        "servicekernelgateway",
        "service gateway",
        "serve",
        "server",
    )
    for _spec_file, data in [*l2_files, *l3_files]:
        for item_id, item in data["items"].items():
            combined = f"{item_id}\n{item['header']}\n{item['body']}".lower()
            if any(signal in combined for signal in service_signals):
                return True
    return False


def assert_bootstrap_preconditions(repo_root: Path, specs_dir: Path) -> None:
    if not specs_dir.exists():
        raise SystemExit("`specs/` is missing. Use the existing BootstrapWorkflow before `vibespec bootstrap impl`.")

    errors, warnings, _coverage = validate.validate_references(specs_dir)
    if warnings:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise SystemExit(f"`specs/` validation failed before bootstrap:\n{joined}")

    src_dir = repo_root / "src"
    if src_dir.exists() and any(path.is_file() for path in src_dir.rglob("*")):
        raise SystemExit("`src/` already contains files. Use `vibespec triage gate` / `vibespec fix gate` instead.")

    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        supported = [
            path for path in tests_dir.rglob("*") if path.suffix.lower() in SUPPORTED_TEST_EXTENSIONS
        ]
        if supported:
            raise SystemExit("`tests/` already contains supported test files. `vibespec bootstrap impl` only handles specs-only repos.")


def language_commands(lang: str) -> tuple[str, str]:
    if lang == "rs":
        return (
            "cargo test --test e2e contracts_ -- --test-threads=1",
            "cargo test --test e2e whitebox_ -- --test-threads=1",
        )
    if lang == "py":
        return (
            "python3 -m pytest -q tests/e2e -k 'contracts_'",
            "python3 -m pytest -q tests/e2e -k 'whitebox_'",
        )
    if lang == "js":
        return (
            "node --test tests/e2e/contracts_*.js",
            "node --test tests/e2e/whitebox_*.js",
        )
    if lang == "ts":
        return (
            "npx tsx --test tests/e2e/contracts_*.ts",
            "npx tsx --test tests/e2e/whitebox_*.ts",
        )
    if lang == "go":
        return (
            "go test ./tests/e2e -run '^TestContracts_'",
            "go test ./tests/e2e -run '^TestWhitebox_'",
        )
    if lang == "cs":
        return (
            "dotnet test tests/E2E.csproj --filter FullyQualifiedName~Contracts_",
            "dotnet test tests/E2E.csproj --filter FullyQualifiedName~Whitebox_",
        )
    raise AssertionError(f"Unhandled language profile `{lang}`")


def black_box_header(lang: str) -> str:
    if lang == "py":
        return (
            '"""ASSERTION INTENT (Black-box tests - public traits and APIs only). '
            'Do not introduce white-box testing logic or internal workarounds."""\n'
        )
    prefix = "//! " if lang == "rs" else f"{COMMENT_PREFIX[lang]} "
    return (
        f"{prefix}ASSERTION INTENT (Black-box tests - public traits and APIs only).\n"
        f"{prefix}Do not introduce white-box testing logic or internal workarounds.\n"
    )


def white_box_header(lang: str) -> str:
    if lang == "py":
        return '"""WHITE-BOX SUPPLEMENTAL COVERAGE. Do not count this file as L1 contract verification."""\n'
    prefix = "//! " if lang == "rs" else f"{COMMENT_PREFIX[lang]} "
    return f"{prefix}WHITE-BOX SUPPLEMENTAL COVERAGE. Do not count this file as L1 contract verification.\n"


def module_comment_lines(lang: str, module: ModuleSpec) -> str:
    prefix = "//! " if lang == "rs" else f"{COMMENT_PREFIX[lang]} "
    lines = [
        f"{prefix}Generated by `vibespec bootstrap impl`.",
        f"{prefix}L2 anchor: `{module.item_id}`",
    ]
    if module.l3_items:
        lines.append(f"{prefix}Related L3 items: {', '.join(sorted(module.l3_items))}")
    lines.append(f"{prefix}{module.summary}")
    return "\n".join(lines) + "\n"


def write_files(repo_root: Path, files: dict[str, str], executable_paths: set[str], force: bool) -> list[str]:
    written = []
    for relative_path, content in files.items():
        target = repo_root / relative_path
        if target.exists() and not force:
            raise SystemExit(f"Refusing to overwrite existing file `{relative_path}` without --force.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if relative_path in executable_paths:
            target.chmod(0o755)
        written.append(relative_path)
    return written


def generate_files(repo_root: Path, lang: str, project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    if lang == "rs":
        return generate_rust_files(project_name, model)
    if lang == "py":
        return generate_python_files(project_name, model)
    if lang == "js":
        return generate_js_files(project_name, model)
    if lang == "ts":
        return generate_ts_files(project_name, model)
    if lang == "go":
        return generate_go_files(project_name, model)
    if lang == "cs":
        return generate_csharp_files(project_name, model)
    raise AssertionError(f"Unhandled language profile `{lang}`")


def generate_common_files(lang: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    files: dict[str, str] = {}
    executable_paths: set[str] = set()
    contracts_command, whitebox_command = language_commands(lang)
    files["scripts/test-workflow.sh"] = render_test_workflow(contracts_command, whitebox_command)
    executable_paths.add("scripts/test-workflow.sh")
    files["specs/gate-profile.json"] = render_gate_profile(
        contract_spec=model.contract_spec_path,
        black_box_glob=f"tests/e2e/contracts_*{TEST_EXT[lang]}",
        white_box_glob=f"tests/e2e/whitebox_*{TEST_EXT[lang]}",
        run_commands=[
            "./scripts/test-workflow.sh contracts",
            "./scripts/test-workflow.sh whitebox",
            "./scripts/test-workflow.sh all",
        ],
    )
    return files, executable_paths


def generate_rust_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    crate_name = safe_distribution_name(project_name)
    crate_ident = crate_name.replace("-", "_")
    files, executable_paths = generate_common_files("rs", model)

    cargo = [
        "[package]",
        f'name = "{crate_name}"',
        'version = "0.1.0"',
        'edition = "2021"',
        "",
        "[lib]",
        'path = "src/lib.rs"',
    ]
    if model.requires_service_entrypoint:
        cargo.extend(["", "[[bin]]", f'name = "{crate_name}"', 'path = "src/main.rs"'])
    files["Cargo.toml"] = "\n".join(cargo) + "\n"

    module_lines = ["#![allow(dead_code)]", ""]
    for module in model.modules:
        module_lines.append(f"pub mod {module.module_slug};")
    module_lines.extend(
        [
            "",
            "pub fn bootstrap_modules() -> &'static [&'static str] {",
            "    &[",
        ]
    )
    for module in model.modules:
        module_lines.append(f'        "{module.item_id}",')
    module_lines.extend(["    ]", "}"])
    files["src/lib.rs"] = "\n".join(module_lines) + "\n"

    for module in model.modules:
        files[f"src/{module.module_slug}.rs"] = (
            module_comment_lines("rs", module)
            + "\n"
            + "#[derive(Debug, Default, Clone)]\n"
            + f"pub struct {module.symbol_name};\n\n"
            + f"impl {module.symbol_name} {{\n"
            + "    pub fn spec_anchor() -> &'static str {\n"
            + f'        "{module.item_id}"\n'
            + "    }\n"
            + "}\n"
        )

    if model.requires_service_entrypoint:
        files["src/main.rs"] = (
            "fn main() {\n"
            + f'    println!("{crate_name} service skeleton");\n'
            + "}\n"
        )

    root_test = []
    for section in model.contract_sections:
        root_test.append(f'#[path = "e2e/contracts_{section.slug}.rs"]')
        root_test.append(f"mod contracts_{section.slug};")
    for module in model.modules:
        root_test.append(f'#[path = "e2e/whitebox_{module.module_slug}.rs"]')
        root_test.append(f"mod whitebox_{module.module_slug};")
    files["tests/e2e.rs"] = "\n".join(root_test) + "\n"

    for section in model.contract_sections:
        body = [black_box_header("rs"), f"use {crate_ident}::*;", ""]
        for leaf in section.leafs:
            test_name = f"contracts_{section.slug}_{leaf.test_name_slug}"
            body.extend(
                [
                    "#[test]",
                    f"fn {test_name}() {{",
                    f'    // @verify_spec("{leaf.item_id}", mode="skeleton")',
                    f'    todo!("Pending black-box assertion for {leaf.item_id}");',
                    "}",
                    "",
                ]
            )
        files[f"tests/e2e/contracts_{section.slug}.rs"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        body = [
            white_box_header("rs"),
            f"use {crate_ident}::{module.module_slug}::{module.symbol_name};",
            "",
            "#[test]",
            f"fn whitebox_{module.module_slug}_scaffold() {{",
            f"    let _ = {module.symbol_name}::default();",
            f'    todo!("Pending white-box coverage for {module.item_id}");',
            "}",
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}.rs"] = "\n".join(body)

    return files, executable_paths


def generate_python_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    package_name = safe_package_name(project_name)
    files, executable_paths = generate_common_files("py", model)
    files["pyproject.toml"] = (
        "[build-system]\n"
        'requires = ["setuptools>=68"]\n'
        'build-backend = "setuptools.build_meta"\n\n'
        "[project]\n"
        f'name = "{safe_distribution_name(project_name)}"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.11"\n\n'
        "[tool.pytest.ini_options]\n"
        'pythonpath = ["src"]\n'
        'testpaths = ["tests"]\n'
    )

    init_lines = ['"""Generated by `vibespec bootstrap impl`."""', ""]
    for module in model.modules:
        init_lines.append(f"from .{module.module_slug} import {module.symbol_name}")
    init_lines.extend(["", "def bootstrap_modules() -> list[str]:", "    return ["])
    for module in model.modules:
        init_lines.append(f'        "{module.item_id}",')
    init_lines.extend(["    ]", ""])
    files[f"src/{package_name}/__init__.py"] = "\n".join(init_lines)

    for module in model.modules:
        files[f"src/{package_name}/{module.module_slug}.py"] = (
            '"""Generated by `vibespec bootstrap impl`."""\n\n'
            + f"class {module.symbol_name}:\n"
            + f'    """L2 anchor: {module.item_id}"""\n\n'
            + f'    spec_anchor = "{module.item_id}"\n'
        )

    if model.requires_service_entrypoint:
        files[f"src/{package_name}/__main__.py"] = (
            "def main() -> None:\n"
            + f'    print("{package_name} service skeleton")\n\n'
            + 'if __name__ == "__main__":\n'
            + "    main()\n"
        )

    files["tests/e2e/__init__.py"] = ""
    for section in model.contract_sections:
        body = [black_box_header("py"), "import pytest", f"import {package_name}", ""]
        for leaf in section.leafs:
            test_name = f"test_contracts_{section.slug}_{leaf.test_name_slug}"
            body.extend(
                [
                    f"def {test_name}() -> None:",
                    f'    # @verify_spec("{leaf.item_id}", mode="skeleton")',
                    f'    pytest.skip("Pending black-box assertion for {leaf.item_id}")',
                    "",
                ]
            )
        files[f"tests/e2e/contracts_{section.slug}.py"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        body = [
            white_box_header("py"),
            "import pytest",
            f"from {package_name}.{module.module_slug} import {module.symbol_name}",
            "",
            f"def test_whitebox_{module.module_slug}_scaffold() -> None:",
            f"    _ = {module.symbol_name}()",
            f'    pytest.skip("Pending white-box coverage for {module.item_id}")',
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}.py"] = "\n".join(body)

    return files, executable_paths


def generate_js_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    package_name = safe_distribution_name(project_name)
    files, executable_paths = generate_common_files("js", model)
    files["package.json"] = json.dumps(
        {
            "name": package_name,
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "contracts": "node --test tests/e2e/contracts_*.js",
                "whitebox": "node --test tests/e2e/whitebox_*.js",
                "test": "bash ./scripts/test-workflow.sh all",
            },
        },
        indent=2,
    ) + "\n"

    index_lines = ["// Generated by `vibespec bootstrap impl`.", ""]
    for module in model.modules:
        index_lines.append(f'export {{ {module.symbol_name} }} from "./{module.module_slug}.js";')
    index_lines.extend(["", "export function bootstrapModules() {", "  return ["])
    for module in model.modules:
        index_lines.append(f'    "{module.item_id}",')
    index_lines.extend(["  ];", "}"])
    files["src/index.js"] = "\n".join(index_lines) + "\n"

    for module in model.modules:
        files[f"src/{module.module_slug}.js"] = (
            module_comment_lines("js", module)
            + "\n"
            + f"export class {module.symbol_name} {{\n"
            + "  static specAnchor() {\n"
            + f'    return "{module.item_id}";\n'
            + "  }\n"
            + "}\n"
        )

    if model.requires_service_entrypoint:
        files["src/main.js"] = f'console.log("{package_name} service skeleton");\n'

    for section in model.contract_sections:
        body = [black_box_header("js"), 'import test from "node:test";', 'import assert from "node:assert/strict";', 'import * as subject from "../../src/index.js";', ""]
        for leaf in section.leafs:
            test_name = f"contracts_{section.slug}_{leaf.test_name_slug}"
            body.extend(
                [
                    f'test("{test_name}", (t) => {{',
                    f'  // @verify_spec("{leaf.item_id}", mode="skeleton")',
                    "  assert.ok(subject.bootstrapModules);",
                    f'  t.skip("Pending black-box assertion for {leaf.item_id}");',
                    "});",
                    "",
                ]
            )
        files[f"tests/e2e/contracts_{section.slug}.js"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        body = [
            white_box_header("js"),
            'import test from "node:test";',
            'import assert from "node:assert/strict";',
            f'import {{ {module.symbol_name} }} from "../../src/{module.module_slug}.js";',
            "",
            f'test("whitebox_{module.module_slug}_scaffold", (t) => {{',
            f"  assert.ok({module.symbol_name});",
            f'  t.skip("Pending white-box coverage for {module.item_id}");',
            "});",
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}.js"] = "\n".join(body)

    return files, executable_paths


def generate_ts_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    package_name = safe_distribution_name(project_name)
    files, executable_paths = generate_common_files("ts", model)
    files["package.json"] = json.dumps(
        {
            "name": package_name,
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "contracts": "tsx --test tests/e2e/contracts_*.ts",
                "whitebox": "tsx --test tests/e2e/whitebox_*.ts",
                "test": "bash ./scripts/test-workflow.sh all",
            },
            "devDependencies": {
                "tsx": "^4.7.0",
                "typescript": "^5.4.0",
            },
        },
        indent=2,
    ) + "\n"
    files["tsconfig.json"] = json.dumps(
        {
            "compilerOptions": {
                "target": "ES2022",
                "module": "NodeNext",
                "moduleResolution": "NodeNext",
                "strict": True,
                "esModuleInterop": True,
            },
            "include": ["src/**/*.ts", "tests/**/*.ts"],
        },
        indent=2,
    ) + "\n"

    index_lines = ["// Generated by `vibespec bootstrap impl`.", ""]
    for module in model.modules:
        index_lines.append(f'export {{ {module.symbol_name} }} from "./{module.module_slug}.ts";')
    index_lines.extend(["", "export function bootstrapModules(): string[] {", "  return ["])
    for module in model.modules:
        index_lines.append(f'    "{module.item_id}",')
    index_lines.extend(["  ];", "}"])
    files["src/index.ts"] = "\n".join(index_lines) + "\n"

    for module in model.modules:
        files[f"src/{module.module_slug}.ts"] = (
            module_comment_lines("ts", module)
            + "\n"
            + f"export class {module.symbol_name} {{\n"
            + "  static specAnchor(): string {\n"
            + f'    return "{module.item_id}";\n'
            + "  }\n"
            + "}\n"
        )

    if model.requires_service_entrypoint:
        files["src/main.ts"] = f'console.log("{package_name} service skeleton");\n'

    for section in model.contract_sections:
        body = [black_box_header("ts"), 'import test from "node:test";', 'import assert from "node:assert/strict";', 'import * as subject from "../../src/index.ts";', ""]
        for leaf in section.leafs:
            test_name = f"contracts_{section.slug}_{leaf.test_name_slug}"
            body.extend(
                [
                    f'test("{test_name}", (t) => {{',
                    f'  // @verify_spec("{leaf.item_id}", mode="skeleton")',
                    "  assert.ok(subject.bootstrapModules);",
                    f'  t.skip("Pending black-box assertion for {leaf.item_id}");',
                    "});",
                    "",
                ]
            )
        files[f"tests/e2e/contracts_{section.slug}.ts"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        body = [
            white_box_header("ts"),
            'import test from "node:test";',
            'import assert from "node:assert/strict";',
            f'import {{ {module.symbol_name} }} from "../../src/{module.module_slug}.ts";',
            "",
            f'test("whitebox_{module.module_slug}_scaffold", (t) => {{',
            f"  assert.ok({module.symbol_name});",
            f'  t.skip("Pending white-box coverage for {module.item_id}");',
            "});",
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}.ts"] = "\n".join(body)

    return files, executable_paths


def generate_go_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    module_path = f"bootstrap/{safe_distribution_name(project_name)}"
    package_name = safe_package_name(project_name)
    files, executable_paths = generate_common_files("go", model)
    files["go.mod"] = f"module {module_path}\n\ngo 1.22\n"

    root_lines = [
        f"package {package_name}",
        "",
        "func BootstrapModules() []string {",
        "    return []string{",
    ]
    for module in model.modules:
        root_lines.append(f'        "{module.item_id}",')
    root_lines.extend(["    }", "}"])
    files["src/bootstrap.go"] = "\n".join(root_lines) + "\n"

    for module in model.modules:
        files[f"src/{module.module_slug}.go"] = (
            module_comment_lines("go", module)
            + "\n"
            + f"package {package_name}\n\n"
            + f"type {module.symbol_name} struct{{}}\n\n"
            + f"func ({module.symbol_name}) SpecAnchor() string {{\n"
            + f'    return "{module.item_id}"\n'
            + "}\n"
        )

    if model.requires_service_entrypoint:
        files["cmd/service/main.go"] = (
            "package main\n\n"
            + 'import "fmt"\n\n'
            + "func main() {\n"
            + f'    fmt.Println("{package_name} service skeleton")\n'
            + "}\n"
        )

    for section in model.contract_sections:
        body = [black_box_header("go"), "package e2e", "", 'import (', '    "testing"', f'    subject "{module_path}/src"', ")", ""]
        for leaf in section.leafs:
            test_name = f"TestContracts_{pascal_case(section.slug)}_{pascal_case(leaf.test_name_slug)}"
            body.extend(
                [
                    f"func {test_name}(t *testing.T) {{",
                    f'    // @verify_spec("{leaf.item_id}", mode="skeleton")',
                    "    _ = subject.BootstrapModules()",
                    f'    t.Skip("Pending black-box assertion for {leaf.item_id}")',
                    "}",
                    "",
                ]
            )
        files[f"tests/e2e/contracts_{section.slug}_test.go"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        body = [
            white_box_header("go"),
            "package e2e",
            "",
            'import (',
            '    "testing"',
            f'    subject "{module_path}/src"',
            ")",
            "",
            f"func TestWhitebox_{pascal_case(module.module_slug)}_Scaffold(t *testing.T) {{",
            f"    _ = subject.{module.symbol_name}{{}}",
            f'    t.Skip("Pending white-box coverage for {module.item_id}")',
            "}",
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}_test.go"] = "\n".join(body)

    return files, executable_paths


def generate_csharp_files(project_name: str, model: SpecModel) -> tuple[dict[str, str], set[str]]:
    namespace = safe_namespace(project_name)
    project_file = f"{namespace}.csproj"
    files, executable_paths = generate_common_files("cs", model)
    output_type = "Exe" if model.requires_service_entrypoint else "Library"
    files[project_file] = (
        '<Project Sdk="Microsoft.NET.Sdk">\n'
        "  <PropertyGroup>\n"
        f"    <TargetFramework>net8.0</TargetFramework>\n"
        f"    <OutputType>{output_type}</OutputType>\n"
        "    <ImplicitUsings>enable</ImplicitUsings>\n"
        "    <Nullable>enable</Nullable>\n"
        "    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>\n"
        "  </PropertyGroup>\n"
        "  <ItemGroup>\n"
        '    <Compile Include="src/**/*.cs" />\n'
        "  </ItemGroup>\n"
        "</Project>\n"
    )
    files["tests/E2E.csproj"] = (
        '<Project Sdk="Microsoft.NET.Sdk">\n'
        "  <PropertyGroup>\n"
        "    <TargetFramework>net8.0</TargetFramework>\n"
        "    <IsPackable>false</IsPackable>\n"
        "    <ImplicitUsings>enable</ImplicitUsings>\n"
        "    <Nullable>enable</Nullable>\n"
        "    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>\n"
        "  </PropertyGroup>\n"
        "  <ItemGroup>\n"
        f'    <ProjectReference Include="../{project_file}" />\n'
        '    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />\n'
        '    <PackageReference Include="xunit" Version="2.7.1" />\n'
        '    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.8" />\n'
        "  </ItemGroup>\n"
        "  <ItemGroup>\n"
        '    <Compile Include="e2e/**/*.cs" />\n'
        "  </ItemGroup>\n"
        "</Project>\n"
    )

    bootstrap_catalog = [
        f"namespace {namespace};",
        "",
        "public static class BootstrapCatalog",
        "{",
        "    public static string[] ModuleAnchors() =>",
        "    [",
    ]
    for module in model.modules:
        bootstrap_catalog.append(f'        "{module.item_id}",')
    bootstrap_catalog.extend(["    ];", "}"])
    files["src/BootstrapCatalog.cs"] = "\n".join(bootstrap_catalog) + "\n"

    for module in model.modules:
        files[f"src/{module.module_slug}.cs"] = (
            module_comment_lines("cs", module)
            + "\n"
            + f"namespace {namespace};\n\n"
            + f"public sealed class {module.symbol_name}\n"
            + "{\n"
            + f'    public static string SpecAnchor => "{module.item_id}";\n'
            + "}\n"
        )

    if model.requires_service_entrypoint:
        files["src/Program.cs"] = (
            f'Console.WriteLine("{namespace} service skeleton");\n'
        )

    for section in model.contract_sections:
        class_name = f"Contracts_{pascal_case(section.slug)}"
        body = [
            black_box_header("cs"),
            "using Xunit;",
            "",
            f"namespace {namespace}.Tests.E2E;",
            "",
            f"public sealed class {class_name}",
            "{",
        ]
        for leaf in section.leafs:
            method_name = f"Contracts_{pascal_case(section.slug)}_{pascal_case(leaf.test_name_slug)}"
            body.extend(
                [
                    f'    [Fact(Skip = "Pending black-box assertion for {leaf.item_id}")]',
                    f"    public void {method_name}()",
                    "    {",
                    f'        // @verify_spec("{leaf.item_id}", mode="skeleton")',
                    f"        _ = {namespace}.BootstrapCatalog.ModuleAnchors();",
                    "    }",
                    "",
                ]
            )
        body.append("}")
        files[f"tests/e2e/contracts_{section.slug}.cs"] = "\n".join(body).rstrip() + "\n"

    for module in model.modules:
        class_name = f"Whitebox_{pascal_case(module.module_slug)}"
        body = [
            white_box_header("cs"),
            "using Xunit;",
            "",
            f"namespace {namespace}.Tests.E2E;",
            "",
            f"public sealed class {class_name}",
            "{",
            f'    [Fact(Skip = "Pending white-box coverage for {module.item_id}")]',
            f"    public void Whitebox_{pascal_case(module.module_slug)}_Scaffold()",
            "    {",
            f"        _ = new {namespace}.{module.symbol_name}();",
            "    }",
            "}",
            "",
        ]
        files[f"tests/e2e/whitebox_{module.module_slug}.cs"] = "\n".join(body)

    return files, executable_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to bootstrap. Defaults to the current working directory.")
    parser.add_argument("--lang", required=True, help="Target implementation language profile.")
    parser.add_argument("--project-name", help="Optional project/package name override.")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    specs_dir = repo_root / "specs"
    lang = normalize_lang(args.lang)
    assert_bootstrap_preconditions(repo_root, specs_dir)
    model = build_spec_model(specs_dir)
    project_name = args.project_name or repo_root.name
    files, executable_paths = generate_files(repo_root, lang, project_name, model)
    written = write_files(repo_root, files, executable_paths, args.force)
    print(
        json.dumps(
            {
                "result": "ok",
                "language": lang,
                "language_display": LANGUAGE_DISPLAY[lang],
                "requires_service_entrypoint": model.requires_service_entrypoint,
                "files_written": written,
                "contract_sections": [section.item_id for section in model.contract_sections],
                "modules": [module.item_id for module in model.modules],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
