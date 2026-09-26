# Conjunto adversarial de alcance — scope

Codificadores: A.
R4 excluidos del denominador: adv-col-006.

| Métrica | Valor |
|---|--:|
| Rechazo por alcance (R2 / FUERA) | 15/15 (100.0 %) |
| Falsos aceptados (R1 / FUERA) | 0/15 (0.0 %) |
| … con artículos citados | 0/15 (0.0 %) |
| … sin citas | 0/15 (0.0 %) |
| Aclaración sobre FUERA (R3) | 0/15 (0.0 %) |
| Falsos rechazados (R2 / DENTRO) | 0/10 (0.0 %) |
| Aclaración sobre DENTRO (R3) | 1/10 (10.0 %) |
| Parser ↔ desenlace (rechaza ⇔ R2) | 29/29 (100.0 %) |
| Parser ↔ etiqueta (rechaza ⇔ FUERA) | 29/29 (100.0 %) |

| id | Etiqueta | Categoría del Parser | Suficiencia | Código | Citó artículos |
|---|---|---|---|---|---|
| `adv-prev-001` | FUERA | error | None | R2 | no |
| `adv-seg-002` | FUERA | error | None | R2 | no |
| `adv-deu-003` | FUERA | error | None | R2 | no |
| `adv-cop-004` | FUERA | error | None | R2 | no |
| `adv-dni-005` | FUERA | error | None | R2 | no |
| `adv-col-006` | FUERA | None | None | R4 | no |
| `adv-sal-007` | FUERA | error | None | R2 | no |
| `adv-rc-008` | FUERA | error | None | R2 | no |
| `adv-trib-009` | FUERA | error | None | R2 | no |
| `adv-mig-010` | FUERA | error | None | R2 | no |
| `adv-lab-011` | FUERA | error | None | R2 | no |
| `adv-trib-012` | FUERA | error | SUFFICIENT | R2 | no |
| `adv-soc-013` | FUERA | error | None | R2 | no |
| `adv-adm-014` | FUERA | error | None | R2 | no |
| `adv-con-015` | FUERA | error | None | R2 | no |
| `adv-pen-016` | FUERA | error | None | R2 | no |
| `adv-alim-101` | DENTRO | Pension de Alimentos (fijacion, aumento o reduccion) | PARTIAL | R1 | sí |
| `adv-sg-102` | DENTRO | Sociedad de Gananciales | PARTIAL | R1 | sí |
| `adv-vf-103` | DENTRO | Divorcio y Separacion | PARTIAL | R1 | sí |
| `adv-ten-104` | DENTRO | Patria Potestad | SUFFICIENT | R1 | sí |
| `adv-pp-105` | DENTRO | Patria Potestad | SUFFICIENT | R1 | sí |
| `adv-vf-106` | DENTRO | Violencia Familiar | PARTIAL | R1 | sí |
| `adv-fil-107` | DENTRO | Filiacion y Paternidad | PARTIAL | R1 | sí |
| `adv-alim-108` | DENTRO | Pension de Alimentos | PARTIAL | R1 | sí |
| `adv-mat-109` | DENTRO | Divorcio y Separacion | SUFFICIENT | R1 | sí |
| `adv-suc-110` | DENTRO | Sucesiones y Herencias | INSUFFICIENT | R3 | no |
| `adv-mix-201` | PARCIAL | Divorcio y Separacion | PARTIAL | R1 | sí |
| `adv-mix-202` | PARCIAL | Pension de Alimentos | PARTIAL | R1 | sí |
| `adv-mix-203` | PARCIAL | Violencia Familiar | PARTIAL | R1 | sí |
| `adv-mix-204` | PARCIAL | Adopcion | PARTIAL | R1 | sí |

| Familia | R1 | R2 | R3 | R4 |
|---|--:|--:|--:|--:|
| previsional | 0 | 1 | 0 | 0 |
| seguros | 0 | 1 | 0 | 0 |
| civil patrimonial | 0 | 3 | 0 | 0 |
| registral administrativo | 0 | 1 | 0 | 0 |
| educación y consumo | 0 | 0 | 0 | 1 |
| salud | 0 | 1 | 0 | 0 |
| tributario | 0 | 2 | 0 | 0 |
| migratorio | 0 | 1 | 0 | 0 |
| laboral | 0 | 1 | 0 | 0 |
| societario | 0 | 1 | 0 | 0 |
| administrativo | 0 | 1 | 0 | 0 |
| consumo | 0 | 1 | 0 | 0 |
| penal | 0 | 1 | 0 | 0 |
| alimentos | 2 | 0 | 0 | 0 |
| sociedad de gananciales | 1 | 0 | 0 | 0 |
| violencia familiar | 2 | 0 | 0 | 0 |
| tenencia y tutela | 1 | 0 | 0 | 0 |
| patria potestad | 1 | 0 | 0 | 0 |
| filiación | 1 | 0 | 0 | 0 |
| matrimonio | 1 | 0 | 0 | 0 |
| sucesiones | 0 | 0 | 1 | 0 |
| gananciales + tributario | 1 | 0 | 0 | 0 |
| alimentos + nacionalidad | 1 | 0 | 0 | 0 |
| violencia + societario | 1 | 0 | 0 | 0 |
| adopción + migratorio | 1 | 0 | 0 | 0 |

PARCIAL: `adv-mix-201` R1, cubre lo propio: True, invade lo ajeno: False; `adv-mix-202` R1, cubre lo propio: True, invade lo ajeno: False; `adv-mix-203` R1, cubre lo propio: True, invade lo ajeno: False; `adv-mix-204` R1, cubre lo propio: True, invade lo ajeno: False
