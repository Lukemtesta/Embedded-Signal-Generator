
#define MAX_FREQUENCY 1000
#define MAX_AMPLITUDE 100
#define HALF_AMPLITUDE 50

const int g_digital_wavetype_pin = 2;     //!< the number of the pushbutton pin
const int g_digital_led_pin = 13;         //!< Default digital pin allocated to arduino debug led
const int g_analog_freq_pin = 0;          //!< Frequency pin for analog input
const int g_analog_ampl_pin = 1;          //!< Amplitude pin for analog input
const int g_pwm_out_pin = 9;              //!< Signal generator output pin

float g_ts = 0;                             //!< Alternative timestamp

int g_wavetype_buffer[3];
int g_wavetype_buffer_count = 0;
int g_wavetype_max_count = 2;

/**
 * \brief Initialise default state of digital pin I/O
 */
void InitialiseDigitalPins()
{
  pinMode(g_digital_led_pin, OUTPUT);
  pinMode(g_digital_wavetype_pin, INPUT);
}

/**
 * Initialise buffer values to 0
 */
void InitialiseBuffer()
{
  for(int i = 0; i < g_wavetype_max_count; ++i)
  {
    g_wavetype_buffer[i] = 0;
  }
}

/**
 * \brief Callback invoked before main thread execution
 */
void setup() 
{
  Serial.begin(9600);

  InitialiseBuffer();
  InitialiseDigitalPins();
}

/**
 * \brief Set the debug LED state
 */
void SetLEDState(bool state)
{
  digitalWrite(g_digital_led_pin, state);
}

/**
 * Generate a value for a sine wave with the given parameters
 */
float CreateSine(float amplitude, float frequency, float phase, float ts, float samplingrate)
{
    phase *= 2 * PI;
    float coeff = 2 * PI * frequency * (ts / samplingrate);

    return amplitude * sin(coeff + phase);
}

/**
 * Generate a value for a sine wave with the given parameters
 */
float CreateSquare(float amplitude, float frequency, float phase, float ts, float samplingrate)
{
    float coeff = CreateSine(amplitude, frequency, phase, ts, samplingrate);

    // no sign method
    if (coeff > amplitude / 2)
    {
      coeff = amplitude;
    }
    else
    {
      coeff = -amplitude;
    }

    return coeff;
}

/**
 * Main thread
 */
void loop() 
{
  // read the state of the pushbutton value:
  int wavetype = digitalRead(g_digital_wavetype_pin);
  float frequency = analogRead(g_analog_freq_pin);

  // Same multiplexer for all analog inputs (thanks arduino for poor hw design). 
  // Time to wait is so long it effects playback of waveform

  // Normalise analog data
  frequency /= 1024.f;
  frequency *= MAX_FREQUENCY;

  // Store data in buffer
  g_wavetype_buffer[++g_wavetype_buffer_count] = (float)wavetype;

  // Accumulate buffer
  float avg = 0;
  for(int i = 0; i < g_wavetype_buffer_count; ++i)
  {
    avg += (float)g_wavetype_buffer[i];
  }
  avg = avg / (float)g_wavetype_buffer_count;

  // Show debug state
  int output = 0;
  if(avg > 0.5)
  {
    SetLEDState(true);
    // range = 0 -> 255
    output = CreateSine(HALF_AMPLITUDE, frequency, 0, g_ts, MAX_FREQUENCY * 2);
    output += HALF_AMPLITUDE;
  }
  else
  {
    SetLEDState(false);
    // range = 0 -> 255
    output = CreateSquare(HALF_AMPLITUDE, frequency, 0, g_ts, MAX_FREQUENCY * 2);
    output += HALF_AMPLITUDE;
  }

  // Write waveform to DAC
  Serial.println(output);
  analogWrite(g_pwm_out_pin, output);

  // Slide buffer
  if(g_wavetype_buffer_count >= 2)
  {
    for(int i = 1; i < g_wavetype_buffer_count; ++i)
    {
      g_wavetype_buffer[i-1] = g_wavetype_buffer[i];
    }
    g_wavetype_buffer[g_wavetype_buffer_count] = 0;
  }

  g_ts += .1;
}
