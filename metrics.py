def indice_jaccard(set_a, set_b):
    interseccion = set_a.intersection(set_b)
    union = set_a.union(set_b)
    if len(union) == 0: return 0.0, set()
    score = (len(interseccion) / len(union)) * 100
    return score, interseccion

def reporte(s_v, s_a, s_t, c_v, c_a, c_t):
    print("\n" + "="*50)
    print("📊 REPORTE FINAL (Ejecución Local)")
    print("="*50)
    print(f"1. 👁️ VISUAL: {s_v:.2f}%  -> {list(c_v)[:3]}")
    print(f"2. 🎤 AUDIO:  {s_a:.2f}%  -> {list(c_a)[:3]}")
    print(f"3. 🔤 TEXTO:  {s_t:.2f}%  -> {list(c_t)[:3]}")
    
    promedio = (s_v + s_a + s_t) / 3
    print("-" * 50)
    print(f"⭐ COMPATIBILIDAD TOTAL: {promedio:.2f}%")
    print("="*50 + "\n")