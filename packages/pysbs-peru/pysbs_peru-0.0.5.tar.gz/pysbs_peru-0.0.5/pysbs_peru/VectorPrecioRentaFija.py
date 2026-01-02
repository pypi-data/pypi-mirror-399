from bs4 import BeautifulSoup 
import pandas as pd



def get_vector_precios(fechaProceso=None, cboMoneda=None, cboEmisor=None, cboRating=None):
    """
    Descarga el Vector de Precios de Renta Fija de la SBS.
    Realiza el mapeo automático de códigos (inputs) a descripciones reales (Excel).
    """

    # --- 0. DICCIONARIOS DE MAPEO (Según tus imágenes) ---
    # Traducen lo que envía el usuario -> Lo que realmente está escrito en el Excel
    
    # Mapeo de Moneda (Imagen image_fda4b2.png)
    # Nota: Usamos strings en las claves porque los inputs suelen llegar como texto
    MAP_MONEDA = {
        '1': 'PEN',
        '2': 'VAC',
        '3': 'USD'
    }

    # Mapeo de Emisor (Imagen image_fdf64d.png)
    MAP_EMISOR = {
        '1000': 'GOB.CENTRAL',
        '2011': 'ALICORP S.A.',
        '0087': 'BANCO FALABELLA',
        '0088': 'BCO RIPLEY',
        '0001': 'BCRP',
        '0011': 'CONTINENTAL',
        '0042': 'CREDISCOTIA',
        '0003': 'INTERBANK'
        # Se pueden agregar más si aparecen en el futuro
    }
    
    # Mapeo de Rating (Imagen image_fda477.png)
    # En este caso el código y la descripción parecen iguales, pero normalizamos por si acaso.
    # Si el usuario manda "A " con espacio, esto ayuda a limpiar.
    # Como la imagen muestra que el valor ES el texto, no necesitamos traducción compleja,
    # pero sí asegurarnos que coincida exactamente.

    # 1. VALIDACIÓN OBLIGATORIA DE FECHA
    if not fechaProceso or not isinstance(fechaProceso, str):
        raise TypeError("❌ Error: 'fechaProceso' es obligatorio y debe ser texto (formato dd/mm/yyyy).")

    # Limpieza de la fecha
    fecha_clean = fechaProceso.strip()
    fecha_clean = fecha_clean.replace("/", ".") 

    # 2. CONSTRUCCIÓN DE LA URL
    base_url = "https://raw.githubusercontent.com/ecandela/pysbs-peru-data/main/vp_rentafija"
    nombre_archivo = f"Renta_Fija_{fecha_clean}.xls"
    url = f"{base_url}/{nombre_archivo}"

    try:
        print(f"1. Descargando: {nombre_archivo}...")

        tablas = pd.read_html(url, flavor='bs4')

        # 2. Como read_html devuelve una lista, tomamos la primera tabla (índice 0)
        df = tablas[0]
        df.columns = df.columns.astype(str).str.strip()
        
     
        # --- 4. LÓGICA DE FILTRADO CON TRADUCCIÓN (MAPEO) ---
        
        # A) FILTRO MONEDA
        if cboMoneda:
            val_input = str(cboMoneda).strip() # Aseguramos que sea string '1', no int 1
            
            # Buscamos la traducción. Si no existe en el mapa, asumimos que el usuario
            # envió el texto directo (ej: envió "Soles" en vez de "1")
            val_real = MAP_MONEDA.get(val_input, val_input)
            
            # Filtramos
            df = df[df['Moneda'] == val_real]

        # B) FILTRO EMISOR
        if cboEmisor:
            val_input = str(cboEmisor).strip()
            
            # El input '0003' a veces llega como '3'. Hacemos zfill para asegurar formato de 4 dígitos si es numérico
            if val_input.isdigit() and len(val_input) < 4:
                val_input = val_input.zfill(4)
            
            # Traducimos código -> Nombre Real (ej: '0003' -> 'INTERBANK')
            val_real = MAP_EMISOR.get(val_input, val_input)
            
            df = df[df['Emisor'] == val_real]

        # C) FILTRO RATING
        if cboRating:
            val_input = str(cboRating).strip()
            # Aquí asumimos que el valor es directo (ej: "AAA"), pero limpiamos espacios
            df = df[df['Rating Emisión'] == val_input]
        
        # 5. VERIFICACIÓN FINAL
        if df.empty:
            print("⚠️ Aviso: La consulta devolvió 0 filas. Verifique si los códigos de filtro son correctos para esta fecha.")
            
        return df.reset_index(drop=True)

    except Exception as e:
        raise RuntimeError(f"Error procesando el vector de precios: {str(e)}") from e

    
def get_html_seleniumbase(url):

    with SB(uc=True, test=True, locale_code="en", headless=False) as sb:

        # Abrir la URL con desconexión controlada
        sb.uc_open_with_disconnect(url, 2.2)
        
        # Simular presionar la tecla Tab y luego Espacio
        sb.uc_gui_press_key("\t")
        sb.uc_gui_press_key(" ")
        
        # Reconectar después de una pausa
        sb.reconnect(2.2)
        
        # Obtener el código HTML de la página
        html_content = sb.get_page_source()
        
        return html_content



def get_df_emisores(fechaProceso=None):
    # 1. Obtienes la data completa
    df = get_vector_precios(fechaProceso=fechaProceso)

    # 2. Creas el DataFrame de emisores únicos y lo ordenas
    df_emisores = pd.DataFrame(df['Emisor'].unique(), columns=['Emisor'])
    df_emisores = df_emisores.sort_values(by='Emisor', ascending=True).reset_index(drop=True)
    return df_emisores


def get_precios_by_isin(isin):

    base_url = "https://raw.githubusercontent.com/ecandela/pysbs-peru-data/main/vp_rentafija/anual"
    nombre_archivo_web = f"vector_precio_2025.parquet"   
    url = f"{base_url}/{nombre_archivo_web}"

    df = pd.read_parquet(url)   
    df = df[df['ISIN/Identif.'] == isin].copy()
    df['Fecha de Proceso (d/m/Y)'] = df['Fecha de Proceso']
    df['Fecha de Proceso'] = pd.to_datetime(df['Fecha de Proceso'], dayfirst=True, errors='coerce')
    df = df.sort_values(by='Fecha de Proceso',ascending=False)
    
    return df


