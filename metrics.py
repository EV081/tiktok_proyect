def indice_jaccard(set_a, set_b):
    """Calcula porcentaje de similitud entre dos conjuntos"""
    interseccion = set_a.intersection(set_b)
    union = set_a.union(set_b)
    
    if len(union) == 0:
        return 0.0, set()
        
    score = (len(interseccion) / len(union)) * 100
    return score, interseccion

def reporte(score_v, score_a, score_t, com_v, com_a, com_t):
    print("\n" + "="*50)
    print("📊 REPORTE FINAL DE COMPATIBILIDAD (Ingeniería de Datos)")
    print("="*50)
    
    print(f"1. 👁️ SIMILITUD VISUAL (Objetos/Escenas): {score_v:.2f}%")
    print(f"   -> Coincidencias: {list(com_v)[:5]}")
    
    print(f"\n2. 🎤 SIMILITUD AUDITIVA (Temas hablados): {score_a:.2f}%")
    print(f"   -> Coincidencias: {list(com_a)[:5]}")

    print(f"\n3. 🔤 SIMILITUD DE TEXTO (Memes/Frases):   {score_t:.2f}%")
    print(f"   -> Coincidencias: {list(com_t)[:5]}")
    
    promedio = (score_v + score_a + score_t) / 3
    print("-" * 50)
    print(f"⭐ COMPATIBILIDAD TOTAL DEL PERFIL: {promedio:.2f}%")
    print("="*50 + "\n")