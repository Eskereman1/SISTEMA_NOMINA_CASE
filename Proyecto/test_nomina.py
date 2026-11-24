# test_nomina.py - Pruebas unitarias de reglas de negocio (Lower CASE / QA)
ISR_TASA = 0.16
IMSS_TASA = 0.0277
CODIGOS_VALIDOS = {"BONO200": 200, "EXTRAPLUS": 500, "ASIS100": 300}

def calcular_nomina(pago_hora, horas_trabajadas, codigo_bono=""):
    horas_normales = min(horas_trabajadas, 40)
    horas_extras = max(0, horas_trabajadas - 40)
    bono = CODIGOS_VALIDOS.get(codigo_bono, 0)
    bruto = (horas_normales * pago_hora) + (horas_extras * pago_hora * 2) + bono
    neto = bruto - (bruto * ISR_TASA) - (bruto * IMSS_TASA)
    return round(bruto, 2), round(neto, 2)

def test_jornada_normal_sin_bono():
    # 40 horas a $100/hr = $4000 bruto -> neto tras 18.77% deducciones = $3249.20
    bruto, neto = calcular_nomina(100, 40)
    assert bruto == 4000.00
    assert neto == 3249.20

def test_caso_19068_horas_extras_y_bono():
    # 45 horas (5 extras al doble) + BONO200 ($200) = $5200 bruto
    bruto, neto = calcular_nomina(100, 45, "BONO200")
    assert bruto == 5200.00
    assert neto == 4223.96

def test_codigo_bono_invalido():
    # Un código inexistente debe sumar $0 de bono sin generar error
    bruto, _ = calcular_nomina(100, 40, "BONO_FALSO")
    assert bruto == 4000.00