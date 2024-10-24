import streamlit as st
import serial
import time
import matplotlib.pyplot as plt
import pandas as pd
import serial.tools.list_ports



# Función para detectar puertos seriales disponibles
def detect_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Configuración del puerto serial
available_ports = detect_serial_ports()
serial_port = st.selectbox('Seleccione el puerto COM:', available_ports)  # Cambia esto por el puerto correcto
baud_rate = 115200
arduino = None

# Variables globales para almacenar los datos
raw_signal_data = []
filtered_signal_data = []
timestamps = []

# Bandera para controlar la toma de datos
is_collecting = False

# Función para iniciar la toma de datos
def start_data_collection():
    global arduino, is_collecting
    if arduino is None:
        arduino = serial.Serial(serial_port, baud_rate, timeout=1)
    is_collecting = True

# Función para detener la toma de datos
def stop_data_collection():
    global is_collecting
    is_collecting = False
    if arduino:
        arduino.close()

# Función para guardar los datos en un archivo de texto
def save_data_to_txt(filename):
    if len(timestamps) == 0:
        st.warning("No hay datos para guardar.")
        return
    with open(filename, 'w') as file:
        file.write("Time(s), Raw Voltage(V), Filtered Voltage(V)\n")
        for i in range(len(timestamps)):
            file.write(f"{timestamps[i]}, {raw_signal_data[i]}, {filtered_signal_data[i]}\n")
    st.success(f"Datos guardados en {filename}")

# Función para leer el puerto serial y extraer los datos
def read_serial_data():
    if arduino and arduino.in_waiting > 0:
        try:
            # Leer línea del monitor serial
            line = arduino.readline().decode('utf-8').strip()
            if line:
                # Parsear la línea esperada del formato: Voltaje entrada: X V Voltaje filtrado: Y V
                parts = line.split('\t')
                raw_volt_str = parts[0].split(": ")[1].replace(" V", "")
                filtered_volt_str = parts[1].split(": ")[1].replace(" V", "")

                raw_voltage = float(raw_volt_str)
                filtered_voltage = float(filtered_volt_str)

                return raw_voltage, filtered_voltage
        except:
            return None, None
    return None, None

# Crear la interfaz gráfica con Streamlit
st.title("Captura de Datos desde Arduino")

# Input para el título del archivo
filename = st.text_input("Ingrese el título para el archivo de salida (sin extensión):", "datos")

# Botones para iniciar y detener la captura
col1, col2 = st.columns(2)
with col1:
    if st.button("Iniciar Captura"):
        start_data_collection()

with col2:
    if st.button("Detener Captura"):
        stop_data_collection()

# Mostrar gráfico en tiempo real
placeholder = st.empty()

# Bucle principal de toma de datos
if is_collecting:
    st.write("Toma de datos en curso...")

    start_time = time.time()  # Registrar el tiempo de inicio

    while is_collecting:
        raw_voltage, filtered_voltage = read_serial_data()
        if raw_voltage is not None and filtered_voltage is not None:
            # Registrar los datos
            current_time = time.time() - start_time
            timestamps.append(current_time)
            raw_signal_data.append(raw_voltage)
            filtered_signal_data.append(filtered_voltage)

            # Actualizar gráfico
            data = pd.DataFrame({
                'Tiempo (s)': timestamps,
                'Voltaje de Entrada (V)': raw_signal_data,
                'Voltaje Filtrado (V)': filtered_signal_data
            })

            plt.figure(figsize=(10, 5))
            plt.plot(data['Tiempo (s)'], data['Voltaje de Entrada (V)'], label='Voltaje de Entrada')
            plt.plot(data['Tiempo (s)'], data['Voltaje Filtrado (V)'], label='Voltaje Filtrado')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Voltaje (V)')
            plt.legend()

            placeholder.pyplot(plt)

        time.sleep(0.01)  # Pequeño delay para evitar saturación del puerto serial

# Guardar los datos en archivo de texto al detener la captura
if not is_collecting and st.button("Guardar Datos"):
    save_data_to_txt(f"{filename}.txt")


