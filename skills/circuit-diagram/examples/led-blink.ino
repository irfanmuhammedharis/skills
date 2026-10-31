// led-blink.ino - pairs with examples/led-blink-breadboard.svg
int ledPin = 13;   // LED on pin 13 (D13)

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
