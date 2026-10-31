#!/usr/bin/env python3
"""Scaffold an empty software-docs-suite skeleton.

Usage:
    python3 scaffold_docs.py <output-dir> --name "Product Name" [--headless]

Creates the numbered .md files, decisions/ (with an example ADR), CHANGELOG.md, and glossary.md,
each with a heading and a one-line pointer to its template. Idempotent-ish: refuses to overwrite an
existing non-empty file so you never clobber real docs.
"""
import argparse
import os
import sys
from datetime import date

FILES = [
    ("README.md", "# {name} — Documentation Suite\n\n<!-- Fill from references/document-templates.md > README.md. Agent reading order: AGENTS.md, README, 00-07, 08-build-plan. -->\n"),
    ("00-product-brief.md", "# Product Brief\n\n<!-- Template: document-templates.md > 00 -->\n"),
    ("01-requirements.md", "# Requirements\n\n<!-- Template: document-templates.md > 01. Every FR needs testable acceptance criteria. -->\n"),
    ("02-architecture.md", "# Architecture\n\n<!-- Template: document-templates.md > 02 -->\n"),
    ("03-data-model.md", "# Data Model\n\n<!-- Template: document-templates.md > 03. Include seed/fixture data. -->\n"),
    ("04-api-spec.md", "# API Specification\n\n<!-- Template: document-templates.md > 04. Full request/response/error per endpoint. -->\n"),
    ("05-ui-ux.md", "# UI / UX\n\n<!-- Template: document-templates.md > 05. Omit if headless. -->\n"),
    ("06-security.md", "# Security\n\n<!-- Template: document-templates.md > 06 -->\n"),
    ("07-testing-strategy.md", "# Testing Strategy\n\n<!-- Write from references/testing-and-verification.md -->\n"),
    ("08-build-plan.md", "# Build Plan\n\n<!-- Template: document-templates.md > 08. Ordered tasks; per-task skill, tests, Definition of Done. -->\n"),
    ("09-deployment-ops.md", "# Deployment & Operations\n\n<!-- Template: document-templates.md > 09 -->\n"),
    ("AGENTS.md", "# AGENTS.md — Operating Manual for the AI Development Agent\n\n<!-- Write from references/agent-instructions.md -->\n"),
    ("glossary.md", "# Glossary\n\n| Term | Definition |\n|------|------------|\n"),
    ("CHANGELOG.md", "# Changelog\n\nAll notable changes per completed build task (Keep a Changelog style).\n\n## [Unreleased]\n"),
]

ADR = """# 0001 — <Title of the decision>

- Status: proposed | accepted | superseded
- Date: {today}

## Context
<The forces at play and the problem being decided.>

## Options considered
- Option A — pros / cons
- Option B — pros / cons

## Decision
<What we chose.>

## Consequences
<What becomes easier/harder as a result.>
"""

def write(path, text):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  skip (exists): {path}")
        return
    with open(path, "w") as f:
        f.write(text)
    print(f"  wrote: {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--name", default="Untitled Product")
    ap.add_argument("--headless", action="store_true", help="omit the UI/UX doc")
    args = ap.parse_args()

    root = args.output_dir
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "decisions"), exist_ok=True)

    print(f"Scaffolding docs suite in {root} for '{args.name}':")
    for fname, tmpl in FILES:
        if args.headless and fname == "05-ui-ux.md":
            continue
        write(os.path.join(root, fname), tmpl.format(name=args.name))
    write(os.path.join(root, "decisions", "0001-example.md"), ADR.format(today=date.today().isoformat()))
    print("Done. Now fill each file using references/document-templates.md.")

if __name__ == "__main__":
    main()
