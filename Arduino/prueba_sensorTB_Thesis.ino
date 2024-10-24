#include <Arduino.h>

/*********************************************  PINES **********************************************/ 
const int TBsensor = A0;  // Pin analógico en Arduino UNO
int led = 13;             // LED en pin 13

/*********************************************  FILTRO **********************************************/ 
// Define filter parameters
const int numTaps = 3;

float b[numTaps] = {0.0156, 0.0311, 0.0156};  // Numerator coefficients, ya que la fs = 230Hz
float a[numTaps] = {1.0, -1.6173, 0.6796}; // Denominator coefficients

// Filter state variables
float x[numTaps] = {0}; // Input buffer
float y[numTaps] = {0}; // Output buffer

// Function to apply the digital filter
float digitalFilter(float input) {
    // Shift input values in buffer
    for (int i = numTaps - 1; i > 0; i--) {
        x[i] = x[i - 1];
        y[i] = y[i - 1];
    }

    // Add new input value to buffer
    x[0] = input;

    // Calculate filter output
    float output = 0;
    for (int i = 0; i < numTaps; i++) {
        output += b[i] * x[i];
        if (i > 0) {
            output -= a[i] * y[i];
        }
    }

    y[0] = output; // Update output buffer

    return output;
}

void setup() {
    // Iniciar la comunicación serie
    Serial.begin(115200);

    // Configurar el LED como salida
    pinMode(led, OUTPUT);

    // Apagar el LED inicialmente
    digitalWrite(led, LOW);
}

void loop() {
    // Lectura del sensor
    float rawInputSignal = analogRead(TBsensor); // Leer el valor analógico del sensor (0 a 1023)

    // Alternar el estado del LED
    digitalWrite(led, HIGH);  // Encender el LED
    delay(500);               // Esperar 500ms
    digitalWrite(led, LOW);   // Apagar el LED
    delay(500);               // Esperar 500ms

    // Aplicar el filtro digital a la señal de entrada
    float filteredSignal = digitalFilter(rawInputSignal);

    // Convertir las lecturas a voltaje (0-5V)
    float voltRawIn = (rawInputSignal / 1023.0) * 5.0;
    float voltFiltIn = (filteredSignal / 1023.0) * 5.0;

    // Imprimir valores en el monitor serie
    Serial.print("Voltaje entrada: ");
    Serial.print(voltRawIn);
    Serial.print(" V\tVoltaje filtrado: ");
    Serial.println(voltFiltIn);

    // Controla la frecuencia de muestreo
    delay(1);
}
