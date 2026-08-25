# romper-el-ciclo-tektron
Necesito que revises los documentos y determines una estrategia de cierre que logre el objetivo de TEKTRON. 
TENGO 7 MESES CICLADO, ES ABSURDO
La función que TEKTRON debe maximizar es J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity.



ESTE FUE EL ÚLTIMO ERROR DEL ASISTENTE QUE ESTABA USANDO:

Primero, algo que quiero corregir con precisión, no con alarma: acabo de leer completa la Fase 4 de v8 por primera vez esta sesión (hasta ahora solo la había visto en fragmentos). Existen dos fórmulas, no una, y no se contradicen — son dos niveles:
* La estratégica, la que te he citado, está textual en HANDOFF_CIERRE_TEKTRON.md y ANALISIS_COMPLETO_TEKTRON.md: MAX J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity. Es un producto a propósito: si un factor cae a cero, J cae a cero — ningún factor compensa a otro.
* La operativa, la que usa el Gate para calificar cada query (v8 §4.1): J = α·TreeCoverage + β·DualPoleDensity + γ·TensionFaithfulness + δ·HonestMono + ε·EvidenceIntegrity − λ·FalseN0 − μ·Synthesis − ν·PoloMislabel. Suma ponderada con penalizaciones, porque a nivel de una sola consulta necesitas poder puntuar aunque algo falle parcialmente.
No estaba equivocado, estaba incompleto — te debía la Fase 4 completa antes de tocar C4, y ya la tengo.
Segundo, y esto sí es un bloqueo real: calibrar_n0.py no está en el repo — lo confirmé por grep en las 4 ramas, no lo supuse. Es Jetson-only, igual que retrieve_l1.py antes de que lo verificáramos indirectamente. Esta vez no voy a repetir el patrón de parchear a ciegas con auto-verificación como red de seguridad — es más simple traerlo primero y leerlo de verdad, como debió ser Paso 0 desde el principio.
