"""Catálogo de reglas iniciales (sección 5 de la especificación funcional).

Es la fuente única de los metadatos de cada regla. La lógica de detección vive
aparte (se enlaza por `code`) y se agrega en el siguiente paso.
"""

from dataclasses import dataclass

from app.models.enums import SeverityLevel


@dataclass(frozen=True)
class RuleSpec:
    code: str
    name: str
    category: str
    severity: SeverityLevel
    description: str
    recommendation: str
    reference: str
    enabled_by_default: bool = True


CATALOG: tuple[RuleSpec, ...] = (
    RuleSpec(
        code="CRYPTO-001",
        name="Potential Hardcoded Secret",
        category="Secrets Management",
        severity=SeverityLevel.HIGH,
        description="Se detectó un posible secreto directamente en el código fuente.",
        recommendation=(
            "Revisa cómo la aplicación gestiona los secretos; "
            "usa variables de entorno o un gestor de secretos."
        ),
        reference="OWASP Secrets Management",
    ),
    RuleSpec(
        code="CRYPTO-002",
        name="Potential Weak Password Hashing",
        category="Password Hashing",
        severity=SeverityLevel.MEDIUM,
        description="Se detectó una función hash que podría usarse para contraseñas.",
        recommendation="Usa Argon2id o bcrypt para almacenar contraseñas.",
        reference="OWASP Password Storage",
    ),
    RuleSpec(
        code="CRYPTO-003",
        name="Cryptographic Configuration Review",
        category="Crypto Configuration",
        severity=SeverityLevel.MEDIUM,
        description="Configuración criptográfica que requiere revisión.",
        recommendation="Verifica la configuración frente a los criterios definidos para el proyecto.",
        reference="NIST SP 800-131A",
    ),
    RuleSpec(
        code="CRYPTO-004",
        name="Key Size Review",
        category="Key Management",
        severity=SeverityLevel.MEDIUM,
        description="Tamaño de clave que requiere revisión.",
        recommendation="Confirma que el tamaño de clave cumpla las recomendaciones vigentes.",
        reference="NIST SP 800-57",
    ),
    RuleSpec(
        code="CRYPTO-005",
        name="Potential Insecure Randomness",
        category="Randomness",
        severity=SeverityLevel.LOW,
        description="Generador aleatorio posiblemente no apto para contextos criptográficos.",
        recommendation="Usa un generador criptográficamente seguro para tokens y claves.",
        reference="OWASP Cryptographic Storage",
    ),
    RuleSpec(
        code="CRYPTO-006",
        name="Potential Exposed Cryptographic Key",
        category="Key Management",
        severity=SeverityLevel.HIGH,
        description="Patrón que podría representar una clave criptográfica expuesta.",
        recommendation="Retira la clave del repositorio y rótala si estuvo expuesta.",
        reference="OWASP Key Management",
    ),
    RuleSpec(
        code="CRYPTO-007",
        name="TLS Configuration Review",
        category="TLS",
        severity=SeverityLevel.LOW,
        description="Configuración TLS sujeta a revisión.",
        recommendation="Revisa versiones y opciones de TLS habilitadas.",
        reference="IETF RFC 8446",
        enabled_by_default=False,
    ),
    RuleSpec(
        code="CRYPTO-008",
        name="Secret in Configuration File",
        category="Secrets Management",
        severity=SeverityLevel.HIGH,
        description="Posible secreto dentro de un archivo de configuración.",
        recommendation="Mueve el secreto fuera del archivo de configuración versionado.",
        reference="OWASP Secrets Management",
    ),
)