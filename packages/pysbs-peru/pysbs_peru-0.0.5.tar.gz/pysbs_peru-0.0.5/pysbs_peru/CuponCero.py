import requests 
import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import requests
import yaml
from datetime import datetime
import pandas as pd
import os


# --- INICIO DE TU LÓGICA DE IMPORTACIÓN ---
try:
    # Intenta importar desde dentro del paquete (uso normal de librería)
    from .settings import config
    print("✅ [CuponCero.py] Configuración cargada desde settings.py")
except ImportError:
    # Fallback: Esto se ejecuta si corres este archivo solo, o si falta settings.py
    print("⚠️ [CuponCero.py] settings.py no encontrado. Usando MockConfig.")
    
    class MockConfig:
        CACHE_DIR = "./cache_temporal"
        TIMEOUT = 10
        DB_HOST = "localhost"
    
    config = MockConfig()

def obtener_datos_sbs():
    """
    Función principal que simula traer datos usando la config.
    """
    print(f"   -> Conectando a: {config.DB_HOST}")
    print(f"   -> Guardando en: {config.CACHE_DIR}")
    print("   -> Datos obtenidos exitosamente.")
    return True







def pivot_curva_cupon_cero_historico(df):
    # 1. Pivotar el DataFrame
    # IMPORTANTE: Agregamos "Fecha Visual" al índice para no perderla
    pivot_df = df.pivot(index=["Fecha de Proceso (d/m/Y)", "Fecha de Proceso"], 
                        columns="Periodo (días)", 
                        values="Tasas (%)").reset_index()

    # 2. Renombrar las columnas (quita el nombre de la jerarquía)
    pivot_df.columns.name = None

    # 3. Definir columnas de metadatos
    non_numeric_columns = ["Fecha de Proceso (d/m/Y)", "Fecha de Proceso"]

    # 4. Identificar columnas numéricas (los plazos)
    numeric_columns = [col for col in pivot_df.columns if col not in non_numeric_columns]

    # --- CORRECCIÓN PRINCIPAL ---
    # Como las columnas ya son números (0, 90, 180...), Python sabe ordenarlas directo.
    # No usamos lambda ni split.
    numeric_columns.sort() 
    # ----------------------------

    # 5. Reordenar columnas: Info primero, Plazos después
    new_columns_order = non_numeric_columns + numeric_columns
    pivot_df = pivot_df[new_columns_order]

    # 6. Convertir las columnas de tasas a numéricas (float)
    pivot_df[numeric_columns] = pivot_df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    pivot_df = pivot_df.sort_values(by=["Fecha de Proceso"], ascending=[False])

    return pivot_df




def get_curva_cupon_cero_historico(fechaInicio=None, fechaFin=None, tipoCurva=None, cache=True):
    """
    Obtiene datos de la curva SBS con opción de caché local.
    
    Args:
        fechaInicio (str): Fecha inicial en formato dd/mm/yyyy.
        fechaFin (str): Fecha final en formato dd/mm/yyyy.
        tipoCurva (str): Nombre de la curva (ej. 'TIP_PR_PEN').
        use_cache (bool): Si es True, guarda y lee años pasados localmente.
    """
    
    # 1. CONFIGURACIÓN DE CACHÉ
    CACHE_DIR = config.CACHE_DIR
    if cache and not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # 2. VALIDACIÓN DE FECHAS
    if not all([fechaInicio, fechaFin, tipoCurva]):
        raise TypeError("❌ Error: 'fechaInicio', 'fechaFin' y 'tipoCurva' son obligatorios.")

    formato = "%d/%m/%Y"
    try:
        inicio_obj = datetime.strptime(fechaInicio.strip(), formato)
        fin_obj = datetime.strptime(fechaFin.strip(), formato)
        if inicio_obj > fin_obj:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")
    except ValueError as e:
        raise TypeError(f"❌ Error en formato de fecha: {str(e)}")

    # 3. IDENTIFICAR AÑOS Y LÍMITES
    anios_a_procesar = range(inicio_obj.year, fin_obj.year + 1)
    anio_actual = datetime.now().year
    
    dfs_acumulados = []
    base_url = f"https://raw.githubusercontent.com/ecandela/pysbs-peru-data/refs/heads/main/curva/anual/{tipoCurva}"

    # 4. PROCESAMIENTO POR AÑO
    for anio in anios_a_procesar:
        nombre_archivo = f"{tipoCurva}_{anio}.parquet"
        ruta_local = os.path.join(CACHE_DIR, nombre_archivo)
        df_temp = None

        # Determinar si podemos usar el archivo local
        # Condiciones: Cache activado AND el año es pasado AND el archivo existe
        usar_local = cache and anio < anio_actual and os.path.exists(ruta_local)

        if usar_local:
            print(f"📂 [Local] Cargando año {anio}...")
            df_temp = pd.read_parquet(ruta_local)
        else:
            # Descarga de GitHub
            url = f"{base_url}/{nombre_archivo}"
            try:
                msg = "Actualizando año actual" if anio == anio_actual else f"Descargando año {anio}"
                print(f"🌐 [GitHub] {msg}...")
                df_temp = pd.read_parquet(url)
                
                # Guardar en caché si está habilitado y es un año pasado
                if cache and anio < anio_actual:
                    df_temp.to_parquet(ruta_local)
                    print(f"💾 [Caché] Año {anio} guardado en disco.")
            except Exception as e:
                print(f"⚠️ No se pudo obtener el año {anio} de GitHub: {e}")

        if df_temp is not None:
            dfs_acumulados.append(df_temp)

    if not dfs_acumulados:
        raise RuntimeError("No se recuperaron datos. Verifique la conexión o el nombre de la curva.")

    # 5. CONSOLIDACIÓN Y FILTRADO FINAL
    df_total = pd.concat(dfs_acumulados, ignore_index=True)
    df_total['Fecha de Proceso'] = pd.to_datetime(df_total['Fecha de Proceso'])
    
    mask = (df_total['Fecha de Proceso'] >= inicio_obj) & (df_total['Fecha de Proceso'] <= fin_obj)
    df_final = df_total.loc[mask].copy()
    
    # Formatear la fecha para facilitar la lectura al usuario
    df_final['Fecha de Proceso (d/m/Y)'] = df_final['Fecha de Proceso'].dt.strftime('%d/%m/%Y')

    df_final = df_final.sort_values(by=['Fecha de Proceso','Periodo (días)'], ascending=[False, True])

    return df_final.reset_index(drop=True)


def get_curva_cupon_cero(fechaProceso=None, tipoCurva=None):
    """
    Descarga el Vector de Precios de Renta Fija de la SBS.
    Realiza el mapeo automático de códigos (inputs) a descripciones reales (Excel).
    """
    
    # Mapeo de Rating (Imagen image_fda477.png)
    # En este caso el código y la descripción parecen iguales, pero normalizamos por si acaso.
    # Si el usuario manda "A " con espacio, esto ayuda a limpiar.
    # Como la imagen muestra que el valor ES el texto, no necesitamos traducción compleja,
    # pero sí asegurarnos que coincida exactamente.

    # 1. VALIDACIÓN OBLIGATORIA DE FECHA
    if not fechaProceso or not isinstance(fechaProceso, str):
        raise TypeError("❌ Error: 'fechaProceso' es obligatorio y debe ser texto (formato dd/mm/yyyy).")
    
    if not tipoCurva or not isinstance(tipoCurva, str):
        raise TypeError("❌ Error: 'tipoCurva' es obligatorio.")

    # Limpieza de la fecha
    fecha_clean = fechaProceso.strip()

    formato = "%d/%m/%Y"

    try:
        # Intenta convertir la cadena a objeto datetime
        fecha_obj = datetime.strptime(fecha_clean, formato)
        
        # Si pasa la línea anterior, es válida. Obtenemos el año:
        anio = fecha_obj.year
        print(f"La fecha es válida. El año es: {anio}")
    except ValueError:
        raise TypeError("❌ Error: la fecha no es válida o no cumple el formato d/m/Y.")

    # 2. CONSTRUCCIÓN DE LA URL

    base_url = f"https://raw.githubusercontent.com/ecandela/pysbs-peru-data/refs/heads/main/curva/anual/{tipoCurva}"    
    nombre_archivo = f"{tipoCurva}_{anio}.parquet"
    url = f"{base_url}/{nombre_archivo}"
  
    try:
        print(f"1. Descargando: {nombre_archivo}...")

        df = pd.read_parquet(url)      
        df['Fecha de Proceso (d/m/Y)'] = df['Fecha de Proceso'].dt.strftime('%d/%m/%Y')
        # --- 4. LÓGICA DE FILTRADO CON TRADUCCIÓN (MAPEO) ---
        df = df[df['Fecha de Proceso (d/m/Y)'] == fecha_clean].copy()        
        
        # 5. VERIFICACIÓN FINAL
        if df.empty:
            print("⚠️ Aviso: La consulta devolvió 0 filas. Verifique si los códigos de filtro son correctos para esta fecha.")
            
        return df.reset_index(drop=True)

    except Exception as e:
        raise RuntimeError(f"Error procesando el vector de precios: {str(e)}") from e


def plot_curva(df):

    df_cup_por_anio = df[df['Periodo (días)'] % 360 == 0].copy()

    df_cup_por_anio["anio"] = df_cup_por_anio['Periodo (días)'] / 360 

    fig = go.Figure(data=go.Scatter(x=df_cup_por_anio.anio, y=df_cup_por_anio["Tasas (%)"], mode='lines+markers',    name='lines+markers'))

    # Obtener los límites mínimo y máximo de los datos en el eje Y
    y_min = df_cup_por_anio["Tasas (%)"].min()
    y_max = df_cup_por_anio["Tasas (%)"].max()

    # Calcular los 8 valores equidistantes entre el límite mínimo y máximo
    y_values = [y_min + (i * (y_max - y_min) / 7) for i in range(8)]

    fig.update_layout(
                    xaxis_title='Años',
                    yaxis_title='Tasas',       
                    yaxis=dict(tickmode='array',  tickvals=y_values, nticks=8, tickfont=dict(size=12), hoverformat='.2f'),         
                    xaxis=dict(type='category', tickfont=dict(size=12), tickangle=90),
                    margin=dict(l=20, r=10, t=20, b=10)
                    )

    fig.show()



def get_pronostico_lineal(conjunto_x,conjunto_y, var_indep ):
    x = var_indep
    f = np.polyfit(conjunto_x, conjunto_y, 1)
    a = f[0]
    b = f[1]
    pronostico = a * x + b

    return pronostico


def get_tasa_interes_por_dias(dias ,df_tasas):

    lb_dias = "Periodo (días)"
    ld_tasas = "Tasas (%)"

    # Valor "x" que deseas buscar
    x = dias
    y = None
    # Si "x" coincide con uno de los valores en la columna "días", entonces se muestra el registro correspondiente
    matching_record = df_tasas[df_tasas[lb_dias] == x]
    if len(matching_record)>0:

        #print(matching_record)
        y = matching_record.loc[: , ld_tasas].values[0]

    else:        
        # Encontrar el registro inferior y el registro superior más próximos a "x" en la columna "días"
        lower_record = df_tasas[df_tasas[lb_dias] <= x].tail(1)
        upper_record = df_tasas[df_tasas[lb_dias] >= x].head(1)

        result = pd.concat([lower_record, upper_record])

        conjunto_x = result[lb_dias]
        conjunto_y = result[ld_tasas]
        
        y = get_pronostico_lineal(conjunto_x,conjunto_y,x)

        #print(result)
    return y        



############# DEPRECATED ###############

def es_cache_curva_historica_desactualizada(tipoCurva,maxima_fehca_cache_local):
    # Tu URL raw de GitHub
    url = "https://raw.githubusercontent.com/ecandela/pysbs-peru-data/refs/heads/main/config.yaml"

    try:
        # 1. Hacemos la petición GET para obtener el contenido texto del archivo
        response = requests.get(url)
        response.raise_for_status() # Lanza un error si la descarga falla (ej. 404)

        # 2. Parseamos el contenido de texto a un diccionario de Python
        # Usamos safe_load para mayor seguridad
        config = yaml.safe_load(response.text)

        str_fecha_max_nube = config['curva_historica'][tipoCurva]
        fecha_max_nube = datetime.strptime(str_fecha_max_nube, '%d/%m/%Y')

        es_superior = fecha_max_nube.date() > maxima_fehca_cache_local.date()
        return es_superior
        
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
    except yaml.YAMLError as e:
        print(f"Error al procesar el archivo YAML: {e}")
    except KeyError as e:
        print(f"Error: La clave {e} no existe en el archivo YAML.")

#https://www.sbs.gob.pe/app/pp/n_CurvaSoberana/CurvaSoberana/ConsultaHistorica
def get_curva_cupon_cero_historico_deprecated(fechaInicio=None, fechaFin=None, tipoCurva=None, 
                                    cache=True, ruta_personalizada=None):
    """
    Descarga, procesa y filtra la curva cupón cero.
    - cache (bool): Si es True, busca primero en disco local.
    - ruta_personalizada (str): Ruta opcional para guardar/leer este archivo específico.
      Si es None, usa la ruta definida en la configuración global (config.CACHE_DIR).
    """
    
    # 1. LISTA BLANCA DE CÓDIGOS VÁLIDOS
    codigos_permitidos = [
        "CBCRPS", "CBCRS", "CCCLD", "CCINFS", 
        "CCPEDS", "CCPSS", "CCPVS", "CCSDF", "CSBCRD"
    ]
    
    # 2. VALIDACIÓN Y LIMPIEZA DE PARAMETRO
    if not isinstance(tipoCurva, str):
        raise TypeError(f"❌ Error: El TipoCurva debe ser texto. Recibido: {tipoCurva}")
        
    codigo_clean = tipoCurva.upper().strip()
    
    if codigo_clean not in codigos_permitidos:
        raise ValueError(f"❌ Error: El tipo '{tipoCurva}' no existe.\n   Opciones válidas: {codigos_permitidos}")

    # --- CONFIGURACIÓN DE CARPETA CACHÉ (JERARQUÍA) ---
    # Prioridad 1: Argumento de la función
    if ruta_personalizada:
        carpeta_cache = ruta_personalizada
    # Prioridad 2: Configuración Global (settings.py / variables de entorno)
    else:
        carpeta_cache = config.CACHE_DIR
    
    # Crea la carpeta si no existe
    # Nota: Si config.CACHE_DIR usa la ruta del usuario (~/.sbs_helper), esto funcionará sin permisos de admin.
    os.makedirs(carpeta_cache, exist_ok=True)

    # Nombre del archivo y ruta completa
    nombre_archivo = f"resultado_curva_cupon_cero_historico_{codigo_clean}.parquet"
    ruta_cache = os.path.join(carpeta_cache, nombre_archivo)

    # --- INTENTO DE CARGA DESDE CACHÉ ---
    if cache:
        if os.path.exists(ruta_cache):
            print(f"⚡ CACHÉ DETECTADO (Parquet): Cargando datos desde '{ruta_cache}'...")
            try:
                # read_parquet mantiene los tipos de datos intactos
                df_cache = pd.read_parquet(ruta_cache)

                maxima_fehca_cache_local = df_cache['Fecha de Proceso'].max()
                esta_desactualizado = es_cache_curva_historica_desactualizada(tipoCurva,maxima_fehca_cache_local)
                if esta_desactualizado ==False:
                    print(f"⚠️ caché actualizada...")
                    # --- FILTRADO ---
                    if fechaInicio:
                        fi = pd.to_datetime(fechaInicio, dayfirst=True)
                        print(f"   -> Filtrando desde: {fi.date()}")
                        df_cache = df_cache[df_cache['Fecha de Proceso'] >= fi]

                    if fechaFin:
                        ff = pd.to_datetime(fechaFin, dayfirst=True)
                        print(f"   -> Filtrando hasta: {ff.date()}")
                        df_cache = df_cache[df_cache['Fecha de Proceso'] <= ff]

                    return df_cache
                else:
                    print(f"⚠️ La caché para el tipo de curva {tipoCurva} está desactualizada. Se procederá a descargar la versión más reciente.")
            except Exception as e:
                print(f"⚠️ Error leyendo caché (se procederá a descargar): {e}")
        else:
            print(f"ℹ️ Modo caché activado, pero el archivo no existe en: {ruta_cache}")
            print("   -> Se procederá a descargar.")

    # 3. CONSTRUCCIÓN DE LA URL DINÁMICA
    base_url = "https://raw.githubusercontent.com/ecandela/pysbs-peru-data/main/curva_historica"
    nombre_archivo_web = f"curva_historica_{codigo_clean}.xlsx"
    url = f"{base_url}/{nombre_archivo_web}"

    try:
        print("1. Descargando archivo desde GitHub...")
        df_raw = pd.read_excel(url, engine='openpyxl') 
        
        # --- LIMPIEZA ---
        df = df_raw.iloc[1:].reset_index(drop=True)
        df.columns = df_raw.iloc[0]
        df.columns = df.columns.astype(str).str.strip()
        
        print(f"2. Filas totales descargadas: {len(df)}")
        
        if 'Fecha de Proceso' not in df.columns:
             raise KeyError(f"❌ Error: No existe la columna 'Fecha de Proceso'. Columnas: {df.columns.tolist()}")

        df['Fecha de Proceso'] = pd.to_datetime(df['Fecha de Proceso'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha de Proceso'])
        
        if df.empty:
            raise ValueError("⚠️ ALERTA: El DataFrame se quedó vacío después de limpiar fechas incorrectas.")


            
        print(f"6. Filas finales después del filtro: {len(df)}")
        
        # --- FINALIZAR ---
        df = df.sort_values('Fecha de Proceso').reset_index(drop=True)
        df['Fecha Visual'] = df['Fecha de Proceso'].dt.strftime('%d/%m/%Y')
        
        cols = ['Fecha Visual', 'Fecha de Proceso'] + [c for c in df.columns if c not in ['Fecha Visual', 'Fecha de Proceso']]
        
        df['Tasas (%)'] = pd.to_numeric(df['Tasas (%)'], errors='coerce')
        df['Plazo (DIAS)'] = pd.to_numeric(df['Plazo (DIAS)'], errors='coerce')
        
        df = df.sort_values(by=['Fecha de Proceso','Plazo (DIAS)'], ascending=[True, True])
        df_final = df[cols]

        # --- GUARDADO AUTOMÁTICO (PERSISTENCIA PARQUET) ---
        print(f"💾 Guardando resultado (Parquet) en: {ruta_cache}")
        df_final.to_parquet(ruta_cache, index=False)

        # --- FILTRADO ---
        if fechaInicio:
            fi = pd.to_datetime(fechaInicio, dayfirst=True)
            print(f"   -> Filtrando desde: {fi.date()}")
            df_final = df_final[df_final['Fecha de Proceso'] >= fi]

        if fechaFin:
            ff = pd.to_datetime(fechaFin, dayfirst=True)
            print(f"   -> Filtrando hasta: {ff.date()}")
            df_final = df_final[df_final['Fecha de Proceso'] <= ff]


        return df_final

    except Exception as e:
        raise RuntimeError(f"Error en el proceso: {str(e)}") from e