void setup() {
  Serial.begin(57600);
  analogWrite(5, 150);
}
void loop() {
  int sensorValue = analogRead(A0);
  Serial.println(sensorValue);
  delay(5);
}
