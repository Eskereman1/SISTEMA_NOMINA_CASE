#Librerias
import sqlite3      # Este me sirve para guardar los datos de los empleados en el documento Nomina que tengo en la carpeta
import pandas as pd   # Mi mayor error, este hace que pueda usar tablas como excel 
import streamlit as st  # Es como HTML que vimos en badillo pero un poco mas compactado
import random       # Este genera lo datos de las horas aleatorias
import base64       # Este busca las fotos a usar 
import os           # Revisa si no estas wey y esten todos los archivos en la carpeta 

#El nombre de la pagina
st.set_page_config(
    page_title="NeoCash - Control de Nomina", 
    layout="centered",                        
    initial_sidebar_state="expanded"          
)

DB_NAME = "nomina.db" # Guardamos el nombre de nuestra base de datos en una variable para no reescribirla

#Base de datos
def inicializar_base_datos():
    conexion = sqlite3.connect(DB_NAME) # Se conecta al archivo de nomina
    cursor = conexion.cursor()          # El mouse manda
    # Es lo que hice en excel pero esta se genera en la propia pagina
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            ID TEXT PRIMARY KEY,
            Nombre TEXT NOT NULL,
            Puesto TEXT,
            Pago_Hora REAL,
            Lunes REAL DEFAULT 0,
            Martes REAL DEFAULT 0,
            Miercoles REAL DEFAULT 0,
            Jueves REAL DEFAULT 0,
            Viernes REAL DEFAULT 0,
            Sabado REAL DEFAULT 0
        )
    """)
    conexion.commit() # Guarda los cambios
    conexion.close()  # Cierra el archivo sin nesecidad de interrumpir como pasaba antes

try:
    inicializar_base_datos()
except Exception as e:
    st.error(f"Error al iniciar la base de datos: {e}") # Muestra un error si algo en el codigo esta mal

#Bonos
CODIGOS_VALIDOS = {
    "BONO200": (200, "Bono Estándar"),      
    "EXTRAPLUS": (500, "Bono de Productividad"),
    "ASIS100": (300, "Compensación Especial")
}
ISR_TASA = 0.16       
IMSS_TASA = 0.0277    
PagoHoEx = 2          
HorasEs = 40          

#Imagenes
def obtener_base64_imagen(ruta_archivo):
    if os.path.exists(ruta_archivo): # Si el archivo "Fondo.jpg" sí está en la carpeta
        with open(ruta_archivo, "rb") as f: # Se abre en modo lectura binaria
            data = f.read()
        return base64.b64encode(data).decode() # Se convierte base64 seguro para CSS
    return "" # Si no encuentra la imagen, regresa texto vacío para que no falle

fondo_base64 = obtener_base64_imagen("Fondo.jpg") # Corremos la orden y guardamos el resultado

#CSS, Edu del futuro, marca cada styles para que te acuerdes de que son :D
def cargarcss(rutacss, base64_img):
    if os.path.exists(rutacss):
        with open(rutacss, "r", encoding="utf-8") as f:
            contenidocss = f.read()

        contenidocss = contenidocss.replace("__FONDO_BASE64__", base64_img)
        st.markdown(f"<style>{contenidocss}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"No se encontro el archivo de estilos: {rutacss}")

cargarcss("style.css", fondo_base64)
         # Es obligatorio para que Streamlit acepte procesar CSS real

#Acceso
if os.path.exists("Logo.png"):
    st.sidebar.image("Logo.png", use_container_width=True)
else:
    st.sidebar.title("NeoCash") # Si no la encuentra pone un emoji o el nombre

st.sidebar.title("Módulos del Sistema")
rol_usuario = st.sidebar.selectbox("Selecciona tu rol para ingresar:", ["Empleado", "Jefe / Administrador"])

acceso_concedido = False

# Si el usuario dice que es el Jefe se le pide una contraseña
if rol_usuario == "Jefe / Administrador":
    CONTRASEÑA_CORRECTA = "4140" 
    password_ingresada = st.sidebar.text_input("Contraseña de acceso:", type="password", placeholder="••••••••")
    
    if password_ingresada == CONTRASEÑA_CORRECTA:
        acceso_concedido = True
        st.sidebar.success("Sesión Iniciada")
    elif password_ingresada != "":
        st.sidebar.error("Credencial Incorrecta") # Aviso si la caga
else:
    acceso_concedido = True # Si es empleado entra luego luego, porque el empleado no edita nada, solo ingresa su ID

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 NeoCash. All rights reserved.") # Derechos de autor pa que no me copien XD

#Empleado
if rol_usuario == "Empleado":
    st.title("SISTEMA DE NÓMINA EMPRESARIAL")
    st.markdown("Portal de Autoservicio de Empleados")
    
    # Creamos un bloque visual para el input del ID de control
    with st.container():
        st.subheader("Localiza tu Información")
        id_buscar = st.text_input("Introduce tu ID de 5 dígitos:", max_chars=5, placeholder="Ej. 00123")#Deberia llevar .number pero mi paciencia dijo que lo dejara asi
    
    # ID ingresado, se busca en la base
    if id_buscar:
        conexion = sqlite3.connect(DB_NAME)
        query = "SELECT * FROM empleados WHERE ID = ?"
        # Gracias a pandas, crea lo que hice en excel
        df_empleado = pd.read_sql_query(query, conexion, params=(id_buscar,))
        conexion.close()
        
        if df_empleado.empty:
            st.error("El ID ingresado no está registrado. Contacta a tu Supervisor.") # Si la tabla volvió vacía
        else:
            nombre = df_empleado['Nombre'].values[0]
            puesto = df_empleado['Puesto'].values[0]
            pago_por_hora_puesto = df_empleado['Pago_Hora'].values[0]
            
            st.info(f"**¡Hola, {nombre}!** | Puesto actual: *{puesto}*") # Banner azul con sus datos
            
            # Se recuperan las horas trabajadas
            lunes = float(df_empleado['Lunes'].values[0])
            martes = float(df_empleado['Martes'].values[0])
            miercoles = float(df_empleado['Miercoles'].values[0])
            jueves = float(df_empleado['Jueves'].values[0])
            viernes = float(df_empleado['Viernes'].values[0])
            sabado = float(df_empleado['Sabado'].values[0])
            
            # Se hace la suma para el total de horas
            horas_totales = sum([lunes, martes, miercoles, jueves, viernes, sabado])
            # si es mas de 0 se cuenta como asistencia y si es menos de cero, FALTOTA
            dias_trabajados = sum([1 for dia in [lunes, martes, miercoles, jueves, viernes, sabado] if dia > 0])
            
            st.markdown("Tu Jornada Registrada")
            c1, c2, c3 = st.columns(3) # 3 columnas para ver mejor los datos
            with c1:
                st.metric(label="Horas Laboradas", value=f"{horas_totales} hrs")
            with c2:
                st.metric(label="Días Asistidos", value=f"{dias_trabajados} días")
            with c3:
                # Los demas datos en forma de resumen o lista
                if horas_totales > HorasEs:
                    st.metric(label="Horas Extras", value=f"+{horas_totales - HorasEs}") # Esta solo es si chambeo de mas
                elif horas_totales < HorasEs:
                    st.metric(label="Horas Faltantes", value=f"-{HorasEs - horas_totales}") # Esta es solo si estuvo de huevon
                else:
                    st.metric(label="Estatus Semanal", value="Completo") # Esta es si cumplio al 100 la chamba

            # Aqui se pide el bono, Edu estan arriba, por si se te olvida
            with st.container():
                codigo_ingresado = st.text_input("¿Tienes un código promocional o bono?", placeholder="Ingresa el código").upper().strip()
            
            bono_total = 0
            tipo_bono = "Ninguno"
            if codigo_ingresado:
                if codigo_ingresado in CODIGOS_VALIDOS:
                    # Si existe el codigo, este lo busca y lo agrega 
                    bono_total, tipo_bono = CODIGOS_VALIDOS[codigo_ingresado]
                    st.toast(f"¡Código aceptado! +${bono_total}") # Aviso de que si es valido 
                else:
                    st.warning("Código no válido.") # Aviso pos de que no es valido

            #Operaciones
            pago_horas_extra = 0
            # Max es para que se mantengan en 0 y si hay algun negativo no calcule mal
            amount_extras = max(0, horas_totales - HorasEs)
            cantidad_faltantes = max(0, HorasEs - horas_totales)

            if horas_totales > HorasEs:
                precio_hora_extra = pago_por_hora_puesto * PagoHoEx # Calcula cuanto vale la hora extra (Sueldo base * 2)
                pago_horas_extra = amount_extras * precio_hora_extra # Multiplica el excedente por el precio doble
                salario_base_ajustado = HorasEs * pago_por_hora_puesto # su sueldo en base a sus horas
            else:
                salario_base_ajustado = horas_totales * pago_por_hora_puesto # Si trabajó menos, solo se le paga lo que hizo

            # Rebajas
            salario_bruto = salario_base_ajustado + pago_horas_extra + bono_total
            monto_isr = salario_bruto * ISR_TASA   # Restamos el 16%
            monto_imss = salario_bruto * IMSS_TASA # Restamos el 2.77%
            salario_neto = salario_bruto - monto_isr - monto_imss # El dinero real

            #Recibo
            encabezado_recibo = (
                f"========================================\n"
                f"          RECIBO DE PAGO SEMANAL          \n"
                f"========================================\n"
                f"Empleado: {nombre} | ID: {id_buscar}\n"
                f"Puesto:   {puesto}\n"
                f"----------------------------------------\n"
                f"Horas requeridas: {HorasEs} | Horas trabajadas: {horas_totales}\n"
            )
            
            # Esta solo sale si se llaman, si no no
            linea_incidencias = ""
            if amount_extras > 0:
                linea_incidencias = f"Horas Extra:      {amount_extras:<22}\n"
            elif cantidad_faltantes > 0:
                linea_incidencias = f"Horas Faltantes:  {cantidad_faltantes:<22}\n"
            
            desglose_financiero = f"----------------------------------------\n"
            desglose_financiero += f"Salario Base Ajustado: ${salario_base_ajustado:>10.2f}\n"
            
            # Igual, solo si la llaman, si no no
            if pago_horas_extra > 0:
                desglose_financiero += f"Pago Horas Extra:      ${pago_horas_extra:>10.2f}\n"
                
            desglose_financiero += (
                f"Bono ({tipo_bono}):   ${bono_total:>10.2f}\n"
                f"----------------------------------------\n"
                f"Salario Bruto:         ${salario_bruto:>10.2f}\n"
                f"----------------------------------------\n"
                f"Retención ISR (16%):  -${monto_isr:>9.2f}\n"
                f"Retención IMSS(2.7%): -${monto_imss:>9.2f}\n"
                f"----------------------------------------\n"
                f"PAGO NETO SEMANAL:     ${salario_neto:>10.2f}\n"
                f"========================================"
            )
            
            recibo_texto = encabezado_recibo + linea_incidencias + desglose_financiero
            
            st.markdown("Comprobante Fiscal")
            st.code(recibo_texto, language="text") # Crea el recibo y lo imprime en pantalla
            
            # se manda a descargar en bloc de notas
            st.download_button(
                label="Descargar Recibo Oficial (.txt)",
                data=recibo_texto,
                file_name=f"recibo_empleado_{id_buscar}.txt",
                mime="text/plain",
                use_container_width=True
            )

#Jefe
else:
    if acceso_concedido: # Validar contraseña
        st.title("SISTEMA DE NÓMINA EMPRESARIAL")
        st.markdown("### Panel de Control de Administración")
        
        # Se crean 3 columnas para el agregado de datos
        tab1, tab2, tab3 = st.tabs(["Capturar Horas Semanales", "Registro de Personal", "Registro Maestro (BD)"])
        
        # Captura y genera aleatoriamente las horas
        with tab1:
            st.subheader("Asignación de Jornadas")
            id_buscar = st.text_input("Busca un empleado por su ID:", max_chars=5, key="id_jefe", placeholder="Ej. 00123")
            
            if id_buscar:
                conexion = sqlite3.connect(DB_NAME)
                query = "SELECT * FROM empleados WHERE ID = ?"
                df_empleado = pd.read_sql_query(query, conexion, params=(id_buscar,))
                conexion.close()
                
                if df_empleado.empty:
                    st.error("El ID ingresado no coincide con ningún miembro de la plantilla.")
                else:
                    nombre = df_empleado['Nombre'].values[0]
                    st.success(f"Empleado Activo: **{nombre}**")
                    
                    # En la memoria cache congela las horas en 0
                    if f"horas_{id_buscar}" not in st.session_state:
                        st.session_state[f"horas_{id_buscar}"] = {
                            'Lunes': float(df_empleado['Lunes'].values[0]),
                            'Martes': float(df_empleado['Martes'].values[0]),
                            'Miercoles': float(df_empleado['Miercoles'].values[0]),
                            'Jueves': float(df_empleado['Jueves'].values[0]),
                            'Viernes': float(df_empleado['Viernes'].values[0]),
                            'Sabado': float(df_empleado['Sabado'].values[0])
                        }

                    # El dado
                    with st.container():
                        st.markdown("**Llenado Inteligente Express**")
                        if st.button("Simular Semana de Trabajo"):
                            # Da horas de 0 a 8 en los 6 dias
                            st.session_state[f"horas_{id_buscar}"] = {
                                'Lunes': float(random.randint(0, 8)), 'Martes': float(random.randint(0, 8)),
                                'Miercoles': float(random.randint(0, 8)), 'Jueves': float(random.randint(0, 8)),
                                'Viernes': float(random.randint(0, 8)), 'Sabado': float(random.randint(0, 8))
                            }
                            st.toast("Horas generadas en el formulario.")

                    # Formulario de Envío Seguro (Para evitar que la web se refresque a cada segundo mientras escribes)
                    with st.form("form_horas_jefe"):
                        st.markdown("#### Ajuste de Celdas de Tiempo")
                        col1, col2, col3 = st.columns(3) # Subdivisión interna en 3 columnas para acomodar los 6 días
                        with col1:
                            lunes = st.number_input("Lunes", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Lunes'])
                            jueves = st.number_input("Jueves", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Jueves'])
                        with col2:
                            martes = st.number_input("Martes", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Martes'])
                            viernes = st.number_input("Viernes", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Viernes'])
                        with col3:
                            miercoles = st.number_input("Miércoles", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Miercoles'])
                            sabado = st.number_input("Sábado", min_value=0.0, max_value=24.0, value=st.session_state[f"horas_{id_buscar}"]['Sabado'])
                        
                        guardar_horas = st.form_submit_button("Guardar Cambios de Horas", use_container_width=True)
                        
                        # Si el jefe le da al botón de guardar del formulario, mandamos la actualización a SQLite
                        if guardar_horas:
                            # Sincronizamos la memoria intermedia con los datos finales escritos en las celdas
                            st.session_state[f"horas_{id_buscar}"] = {
                                'Lunes': lunes, 'Martes': martes, 'Miercoles': miercoles,
                                'Jueves': jueves, 'Viernes': viernes, 'Sabado': sabado
                            }
                            conexion = sqlite3.connect(DB_NAME)
                            cursor = conexion.cursor()
                            try:
                                # Ejecutamos la actualización basándonos en el ID de control seleccionado
                                cursor.execute("""
                                    UPDATE empleados 
                                    SET Lunes = ?, Martes = ?, Miercoles = ?, Jueves = ?, Viernes = ?, Sabado = ?
                                    WHERE ID = ?
                                """, (lunes, martes, miercoles, jueves, viernes, sabado, id_buscar))
                                conexion.commit()
                                st.success(f"Horas guardadas con éxito para {nombre}.")
                            except sqlite3.Error as e:
                                st.error(f"Error: {e}")
                            finally:
                                conexion.close()

        # Registro
        with tab2:
            st.subheader("Registro de Nuevas Vacantes")
            with st.form("form_empleado", clear_on_submit=True):
                id_nuevo = st.text_input("ID de Control (Exactamente 5 dígitos):", max_chars=5, placeholder="Ej. 00101")
                nombre_nuevo = st.text_input("Nombre Completo del Trabajador:")
                puesto_nuevo = st.text_input("Puesto Asignado:")
                pago_nuevo_texto = st.text_input("Sueldo Base por Hora ($):", placeholder="Ej. 150.00")
                
                enviar = st.form_submit_button("Sincronizar Empleado", use_container_width=True)
                
                if enviar:
                    es_numero_valido = True
                    pago_convertido = 0.0
                    if pago_nuevo_texto:
                        try:
                            pago_convertido = float(pago_nuevo_texto)
                            if pago_convertido < 0:
                                es_numero_valido = False
                        except ValueError:
                            es_numero_valido = False

                    if not id_nuevo or not nombre_nuevo or not puesto_nuevo or not pago_nuevo_texto:
                        st.warning("Hay campos vacíos en el formulario.")
                    elif len(id_nuevo) != 5 or not id_nuevo.isdigit():
                        st.error("El ID deben ser exactamente 5 números.")
                    elif any(char.isdigit() for char in nombre_nuevo) or any(char.isdigit() for char in puesto_nuevo):
                        st.error("Los campos de texto no deben contener números.")
                    elif not es_numero_valido:
                        st.error("El sueldo debe ser positivo.")
                    else:
                        conexion = sqlite3.connect(DB_NAME)
                        cursor = conexion.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO empleados (ID, Nombre, Puesto, Pago_Hora)
                                VALUES (?, ?, ?, ?)
                                ON CONFLICT(ID) DO UPDATE SET
                                    Nombre=excluded.Nombre, Puesto=excluded.Puesto, Pago_Hora=excluded.Pago_Hora
                            """, (id_nuevo, nombre_nuevo, puesto_nuevo, pago_convertido))
                            conexion.commit()
                            st.success(f"Registro maestro de **{nombre_nuevo}** guardado.")
                        except sqlite3.Error as e:
                            st.error(f"Error: {e}")
                        finally:
                            conexion.close()

        with tab3:
            st.subheader("Base de Datos Global")
            conexion = sqlite3.connect(DB_NAME)
            df_global = pd.read_sql_query("SELECT * FROM empleados", conexion)
            conexion.close()
            
            if df_global.empty:
                st.info("No se registran empleados activos.")
            else:
                st.dataframe(df_global, use_container_width=True)
                
    else:
        st.title("Acceso Denegado")
        st.warning("Introduce la contraseña correcta en la barra lateral izquierda para desbloquear las herramientas.")