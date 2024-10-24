import streamlit as st
import serial
import time
import matplotlib.pyplot as plt
import pandas as pd

# Configuración del puerto serial
serial_port = "COM3"  # Cambia esto por el puerto correcto
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
    try:
        if arduino is None or not arduino.is_open:
            arduino = serial.Serial(serial_port, baud_rate, timeout=1)
        is_collecting = True
        st.success("Captura de datos iniciada")
    except serial.SerialException as e:
        st.error(f"Error al abrir el puerto serial: {e}")
        is_collecting = False


# Función para detener la toma de datos
def stop_data_collection():
    global is_collecting, arduino
    is_collecting = False
    if arduino and arduino.is_open:
        arduino.close()
    st.success("Captura de datos detenida")


# Función para guardar los datos en un archivo de texto
def save_data_to_txt(filename):
    try:
        with open(filename, 'w') as file:
            file.write("Time(s), Raw Voltage(V), Filtered Voltage(V)\n")
            for i in range(len(timestamps)):
                file.write(f"{timestamps[i]}, {raw_signal_data[i]}, {filtered_signal_data[i]}\n")
        st.success(f"Datos guardados en {filename}")
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")


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
        except Exception as e:
            st.error(f"Error al leer los datos: {e}")
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

