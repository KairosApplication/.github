#!/usr/bin/env python3
"""Java route extraction helpers; target paths are supplied by sync_org_docs."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTROLLERS = ROOT / "src/main/java/com/kairos/kairosapipostgres/controller"
SECURITY = ROOT / "src/main/java/com/kairos/kairosapipostgres/config/SecurityConfig.java"
DOCS = ROOT / "docs"
START = "<!-- docs-bot:start -->"
END = "<!-- docs-bot:end -->"
MAPPING = re.compile(
    r"@(?P<verb>Get|Post|Put|Patch|Delete)Mapping\b(?:\s*\((?P<args>[^)]*)\))?",
    re.DOTALL,
)
LITERAL = re.compile(r'\s*(?:(?:value|path)\s*=\s*)?"([^"]*)"\s*', re.DOTALL)
BASE = re.compile(r"@RequestMapping\b\s*\(([^)]*)\)", re.DOTALL)


def read_file(path: Path) -> tuple[str, str]:
    with path.open("r", encoding="utf-8", newline="") as file:
        raw = file.read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), newline


def write_if_changed(path: Path, text: str, newline: str = "\n") -> bool:
    normalized = text.rstrip("\n") + "\n"
    if path.exists():
        old, old_newline = read_file(path)
        if old == normalized:
            return False
        newline = old_newline
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(normalized.replace("\n", newline))
    return True


def mapped_path(annotation: str, source: Path) -> str:
    match = LITERAL.fullmatch(annotation)
    if not match:
        raise ValueError(f"Mapeamento não suportado em {source}: {annotation.strip()}")
    return match.group(1)


def endpoints() -> list[tuple[str, str, str]]:
    result = []
    for source in sorted(CONTROLLERS.glob("*Controller.java")):
        code = source.read_text(encoding="utf-8")
        bases = BASE.findall(code)
        if len(bases) != 1:
            raise ValueError(f"Esperado um @RequestMapping de classe em {source}")
        base = mapped_path(bases[0], source)
        matches = list(MAPPING.finditer(code))
        if not matches:
            raise ValueError(f"Nenhuma rota encontrada em {source}")
        for match in matches:
            suffix = mapped_path(match.group("args") or '""', source)
            path = "/" + "/".join(
                part for part in (base + "/" + suffix).split("/") if part
            )
            result.append((match.group("verb").upper(), path, source.name))
    if not result:
        raise ValueError(f"Nenhum controller encontrado em {CONTROLLERS}")
    security = SECURITY.read_text(encoding="utf-8")
    login = re.search(r'\.loginProcessingUrl\s*\(\s*"([^"]+)"\s*\)', security)
    if login:
        result.append(("POST", login.group(1), SECURITY.name))
    return sorted(result, key=lambda item: (item[1], item[0], item[2]))


def api_reference(routes: list[tuple[str, str, str]]) -> str:
    swagger = "swagger.md"
    lines = [
        "# Referência de rotas",
        "",
        "Gerada automaticamente a partir dos controllers e da rota de login do Spring Security.",
        f"Consulte o [Swagger UI]({swagger}) para contratos, parâmetros e respostas.",
        "",
        "| Método | Rota | Controller |",
        "| --- | --- | --- |",
    ]
    for verb, path, controller in routes:
        package = "config" if controller == SECURITY.name else "controller"
        source = f"src/main/java/com/kairos/kairosapipostgres/{package}/{controller}"
        link = f"../{source}"
        lines.append(f"| `{verb}` | `{path}` | [{controller}]({link}) |")
    return "\n".join(lines) + "\n"


def project_versions() -> tuple[str, str]:
    pom = ET.parse(ROOT / "pom.xml").getroot()
    namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
    java = pom.findtext("m:properties/m:java.version", namespaces=namespace)
    boot = pom.findtext("m:parent/m:version", namespaces=namespace)
    if not java or not boot:
        raise ValueError("Versões de Java ou Spring Boot ausentes no pom.xml")
    return java, boot


def marked_section(text: str, body: str, before: str) -> str:
    block = f"{START}\n{body.rstrip()}\n{END}"
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError("Marcadores de documentação incompletos ou duplicados")
        if text.index(START) > text.index(END):
            raise ValueError("Marcadores de documentação fora de ordem")
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
        return pattern.sub(lambda _: block, text, count=1)
    position = text.find(before)
    if position < 0:
        raise ValueError(f"Âncora para inserir documentação não encontrada: {before}")
    return text[:position].rstrip("\n") + "\n\n" + block + "\n\n" + text[position:]
